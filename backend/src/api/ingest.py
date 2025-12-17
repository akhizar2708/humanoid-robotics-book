# backend/src/api/ingest.py
"""Document ingestion endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List
import time

from ..models.documents import IngestRequest, IngestResponse, IngestError, IngestionStatus, ModuleStats, StorageUsage
from ..services.ingestion import ingest_file
from ..db.postgres_client import postgres_client

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_content(request: IngestRequest):
    """
    Ingest book content: parse MDX, chunk, embed, and store.

    Process:
    1. Validate and sanitize input
    2. Parse MDX and extract text
    3. Chunk using RecursiveCharacterTextSplitter (1024 tokens, 128 overlap)
    4. Generate embeddings for each chunk (batched)
    5. Store in Qdrant (vectors) + Postgres (metadata)
    6. Return ingestion statistics
    """
    start_time = time.time()

    # Input validation
    if not request.content_files:
        raise HTTPException(status_code=400, detail="No content files provided")

    if len(request.content_files) > 100:
        raise HTTPException(status_code=400, detail="Too many files in single request (max 100)")

    for content_file in request.content_files:
        # Validate file path
        if not content_file.file_path or not content_file.file_path.strip():
            raise HTTPException(status_code=400, detail="File path cannot be empty")

        # Validate file path doesn't contain directory traversal
        if ".." in content_file.file_path or content_file.file_path.startswith("/"):
            raise HTTPException(status_code=400, detail="Invalid file path (potential security risk)")

        # Validate content
        if not content_file.content or not content_file.content.strip():
            raise HTTPException(status_code=400, detail=f"Content cannot be empty for {content_file.file_path}")

        if len(content_file.content) > 1_000_000:  # 1MB limit
            raise HTTPException(status_code=400, detail=f"Content too large for {content_file.file_path} (max 1MB)")

        # Validate metadata
        if not content_file.metadata.module_id or not content_file.metadata.module_id.strip():
            raise HTTPException(status_code=400, detail=f"module_id required for {content_file.file_path}")

        if not content_file.metadata.chapter_id or not content_file.metadata.chapter_id.strip():
            raise HTTPException(status_code=400, detail=f"chapter_id required for {content_file.file_path}")

    total_chunks = 0
    total_embeddings = 0
    total_skipped = 0
    errors: List[IngestError] = []

    for content_file in request.content_files:
        try:
            chunks_created, embeddings_generated = await ingest_file(
                file_path=content_file.file_path,
                content=content_file.content,
                module_id=content_file.metadata.module_id,
                chapter_id=content_file.metadata.chapter_id,
                section_title=content_file.metadata.section_title,
                page_url=content_file.metadata.page_url,
            )

            total_chunks += chunks_created
            total_embeddings += embeddings_generated

            if chunks_created == 0 and embeddings_generated == 0:
                total_skipped += 1

        except Exception as e:
            errors.append(IngestError(
                file_path=content_file.file_path,
                error_code="INGESTION_ERROR",
                message=str(e),
                details={"error_type": type(e).__name__}
            ))

    processing_time = int((time.time() - start_time) * 1000)

    # Determine status
    if len(errors) == len(request.content_files):
        status = "failed"
    elif errors:
        status = "partial"
    else:
        status = "success"

    return IngestResponse(
        chunks_created=total_chunks,
        embeddings_generated=total_embeddings,
        skipped_unchanged=total_skipped,
        status=status,
        processing_time_ms=processing_time,
        errors=errors
    )


@router.get("/ingest/status", response_model=IngestionStatus)
async def get_ingestion_status():
    """
    Get ingestion statistics: total chunks, per-module stats, storage usage.
    """
    # Total chunks and embeddings
    total_result = await postgres_client.fetchrow(
        "SELECT COUNT(*) as total FROM book_content"
    )
    total_chunks = total_result["total"] if total_result else 0

    # Per-module statistics
    module_results = await postgres_client.fetch("""
        SELECT
            module_id,
            COUNT(*) as chunk_count,
            MAX(created_at) as last_updated
        FROM book_content
        GROUP BY module_id
        ORDER BY module_id
    """)

    modules = [
        ModuleStats(
            module_id=row["module_id"],
            chunk_count=row["chunk_count"],
            last_updated=row["last_updated"].isoformat() if row["last_updated"] else ""
        )
        for row in module_results
    ]

    # Storage usage (estimated)
    storage_result = await postgres_client.fetchrow("""
        SELECT pg_size_pretty(pg_total_relation_size('book_content')) as size_pretty,
               pg_total_relation_size('book_content') as size_bytes
        FROM book_content
        LIMIT 1
    """)

    postgres_mb = 0.0
    if storage_result and storage_result.get("size_bytes"):
        postgres_mb = storage_result["size_bytes"] / (1024 * 1024)

    # Qdrant storage estimate (1536 floats * 4 bytes per chunk)
    qdrant_mb = (total_chunks * 1536 * 4) / (1024 * 1024) if total_chunks > 0 else 0.0

    # Last ingestion time
    last_ingestion_result = await postgres_client.fetchrow(
        "SELECT MAX(created_at) as last_ingestion FROM book_content"
    )
    last_ingestion = ""
    if last_ingestion_result and last_ingestion_result.get("last_ingestion"):
        last_ingestion = last_ingestion_result["last_ingestion"].isoformat()

    return IngestionStatus(
        total_chunks=total_chunks,
        total_embeddings=total_chunks,  # Assume 1:1
        modules=modules,
        storage_usage=StorageUsage(
            qdrant_mb=round(qdrant_mb, 2),
            postgres_mb=round(postgres_mb, 2)
        ),
        last_ingestion=last_ingestion
    )
