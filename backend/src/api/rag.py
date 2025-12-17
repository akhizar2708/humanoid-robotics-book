# backend/src/api/rag.py
"""RAG query endpoints."""

from fastapi import APIRouter, HTTPException
import time
import uuid

from ..models.queries import QueryRequest, QueryResponse, Citation, RetrievedChunk
from ..services.embedder import embed_text
from ..services.retriever import retrieve_chunks, retrieve_scoped
from ..services.generator import generate_answer
from ..services.citation_extractor import extract_citations
from ..db.postgres_client import postgres_client

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_book(request: QueryRequest):
    """
    Query book content with RAG.

    Process:
    1. Validate and sanitize input
    2. Generate embedding for query
    3. Retrieve relevant chunks (global or selected-text scoped)
    4. Generate answer using LLM with strict grounding
    5. Extract citations
    6. Log retrieval for analytics
    """
    start_time = time.time()

    # Input validation
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 1000:
        raise HTTPException(status_code=400, detail="Query too long (max 1000 characters)")

    if request.query_scope not in ["global", "selected"]:
        raise HTTPException(status_code=400, detail="Invalid query_scope. Must be 'global' or 'selected'")

    if request.query_scope == "selected" and not request.selected_text:
        raise HTTPException(status_code=400, detail="selected_text required when query_scope is 'selected'")

    if request.selected_text and len(request.selected_text) > 5000:
        raise HTTPException(status_code=400, detail="Selected text too long (max 5000 characters)")

    if request.top_k < 1 or request.top_k > 20:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")

    # Sanitize input (strip leading/trailing whitespace)
    query = request.query.strip()

    try:
        # Step 1: Generate query embedding
        query_embedding = await embed_text(query, use_cache=True)
        retrieval_start = time.time()

        # Step 2: Retrieve relevant chunks
        if request.query_scope == "selected" and request.selected_text:
            chunks = await retrieve_scoped(
                query_embedding=query_embedding,
                selected_text=request.selected_text,
                top_k=request.top_k
            )
        else:
            chunks = await retrieve_chunks(
                query_embedding=query_embedding,
                top_k=request.top_k
            )

        retrieval_time = int((time.time() - retrieval_start) * 1000)

        # Handle case where no chunks found
        if not chunks:
            return QueryResponse(
                answer="I don't have enough information in the book to answer this question accurately.",
                citations=[],
                retrieved_chunks=[],
                confidence=0.0
            )

        # Step 3: Generate answer
        generation_start = time.time()
        answer, confidence = await generate_answer(
            user_query=request.query,
            retrieved_chunks=chunks
        )
        generation_time = int((time.time() - generation_start) * 1000)

        # Step 4: Extract citations
        citations = await extract_citations(answer)

        # Step 5: Format retrieved chunks for response
        retrieved_chunks_response = [
            RetrievedChunk(
                chunk_id=chunk["chunk_id"],
                score=chunk["score"],
                content_preview=chunk["content_text"][:200] + "..." if len(chunk["content_text"]) > 200 else chunk["content_text"]
            )
            for chunk in chunks
        ]

        # Step 6: Log retrieval to database
        total_time = int((time.time() - start_time) * 1000)
        await log_retrieval(
            session_id=request.session_id,
            query_text=request.query,
            query_embedding=query_embedding,
            query_scope=request.query_scope,
            selected_text=request.selected_text,
            top_k_requested=request.top_k,
            top_k_results=chunks,
            retrieval_time_ms=retrieval_time,
            generation_time_ms=generation_time,
            total_time_ms=total_time
        )

        return QueryResponse(
            answer=answer,
            citations=[
                Citation(**citation) for citation in citations
            ],
            retrieved_chunks=retrieved_chunks_response,
            confidence=confidence
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "QUERY_ERROR",
                "message": f"Failed to process query: {str(e)}",
                "details": {"error_type": type(e).__name__}
            }
        )


async def log_retrieval(
    session_id: uuid.UUID,
    query_text: str,
    query_embedding: list,
    query_scope: str,
    selected_text: str | None,
    top_k_requested: int,
    top_k_results: list,
    retrieval_time_ms: int,
    generation_time_ms: int,
    total_time_ms: int
):
    """Log retrieval to database for analytics."""
    import json

    # Format top_k_results as JSONB
    results_json = json.dumps([
        {
            "chunk_id": chunk["chunk_id"],
            "score": chunk["score"],
            "module_id": chunk["module_id"],
            "chapter_id": chunk["chapter_id"]
        }
        for chunk in top_k_results
    ])

    try:
        await postgres_client.execute(
            """
            INSERT INTO retrieval_log (
                session_id, query_text, query_embedding, query_scope, selected_text,
                top_k_requested, top_k_results, retrieval_time_ms,
                generation_time_ms, total_time_ms
            ) VALUES ($1, $2, $3::vector, $4::query_scope, $5, $6, $7::jsonb, $8, $9, $10)
            """,
            str(session_id), query_text, query_embedding, query_scope, selected_text,
            top_k_requested, results_json, retrieval_time_ms,
            generation_time_ms, total_time_ms
        )
    except Exception as e:
        # Log error but don't fail the query
        print(f"Failed to log retrieval: {e}")
