# backend/src/services/retriever.py
"""Vector similarity search using Qdrant."""

from typing import List, Dict, Any, Optional
from ..db.qdrant_client import qdrant_client

async def retrieve_chunks(
    query_embedding: List[float],
    top_k: int = 5,
    score_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Retrieve similar chunks using vector similarity search (global query).

    Args:
        query_embedding: Query embedding vector (1536 dims)
        top_k: Number of chunks to retrieve
        score_threshold: Minimum similarity score (0-1)

    Returns:
        List of retrieved chunks with metadata and scores
    """
    results = await qdrant_client.search(
        query_vector=query_embedding,
        limit=top_k,
        score_threshold=score_threshold
    )

    chunks = []
    for result in results:
        chunks.append({
            "chunk_id": str(result.id),
            "score": result.score,
            "content_text": result.payload.get("content_text", ""),
            "module_id": result.payload.get("module_id", ""),
            "chapter_id": result.payload.get("chapter_id", ""),
            "section_title": result.payload.get("section_title", ""),
            "page_url": result.payload.get("page_url", ""),
        })

    return chunks


async def retrieve_scoped(
    query_embedding: List[float],
    selected_text: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve chunks scoped to selected text (selected-text query).

    Args:
        query_embedding: Query embedding vector
        selected_text: Text selected by user
        top_k: Number of chunks to retrieve

    Returns:
        List of chunks containing selected text, ranked by similarity
    """
    # Over-query to allow filtering
    results = await qdrant_client.search(
        query_vector=query_embedding,
        limit=top_k * 3,  # Get more results to filter
        score_threshold=0.5  # Lower threshold for broader search
    )

    # Filter to chunks containing selected text (fuzzy match)
    scoped_chunks = []
    normalized_selected = ' '.join(selected_text.lower().split())

    for result in results:
        chunk_text = result.payload.get("content_text", "")
        normalized_chunk = ' '.join(chunk_text.lower().split())

        # Check if selected text appears in chunk
        if normalized_selected in normalized_chunk:
            scoped_chunks.append({
                "chunk_id": str(result.id),
                "score": result.score,
                "content_text": chunk_text,
                "module_id": result.payload.get("module_id", ""),
                "chapter_id": result.payload.get("chapter_id", ""),
                "section_title": result.payload.get("section_title", ""),
                "page_url": result.payload.get("page_url", ""),
            })

            if len(scoped_chunks) >= top_k:
                break

    return scoped_chunks


async def retrieve_by_section(
    query_embedding: List[float],
    module_id: str,
    chapter_id: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve chunks filtered to specific module/chapter (alternative scoping method).

    Args:
        query_embedding: Query embedding vector
        module_id: Module identifier (e.g., "module-1")
        chapter_id: Chapter identifier (e.g., "chapter-1")
        top_k: Number of chunks to retrieve

    Returns:
        List of chunks from specified section, ranked by similarity
    """
    # TODO: Implement Qdrant filtering by module_id and chapter_id
    # This requires Qdrant filter support which needs to be added to the client wrapper
    raise NotImplementedError("Section-based filtering not yet implemented")
