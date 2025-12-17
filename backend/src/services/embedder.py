# backend/src/services/embedder.py
"""OpenAI embedding generation with TTL caching."""

from openai import AsyncOpenAI
from cachetools import TTLCache
import hashlib
from typing import List
import os

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
)

# In-memory cache for query embeddings (TTL: 1 hour)
query_cache = TTLCache(maxsize=1000, ttl=3600)

async def embed_text(text: str, use_cache: bool = True) -> List[float]:
    """
    Generate embedding for a single text using OpenAI text-embedding-3-small.

    Args:
        text: Text to embed
        use_cache: Whether to use cache (default True for queries, False for documents)

    Returns:
        1536-dimensional embedding vector
    """
    if use_cache:
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in query_cache:
            return query_cache[cache_key]

    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    embedding = response.data[0].embedding

    if use_cache:
        query_cache[cache_key] = embedding

    return embedding


async def embed_chunks_batch(chunks: List[str], batch_size: int = 20) -> List[List[float]]:
    """
    Batch embed multiple chunks to reduce API calls (for document ingestion).

    Args:
        chunks: List of text chunks to embed
        batch_size: Number of chunks per API request (max 2048 for OpenAI)

    Returns:
        List of embedding vectors (same order as input chunks)
    """
    all_embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=batch,  # OpenAI supports batching up to 2048 inputs
        )

        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def clear_cache():
    """Clear the embedding cache (useful for testing)."""
    query_cache.clear()
