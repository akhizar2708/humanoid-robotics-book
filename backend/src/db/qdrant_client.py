# backend/src/db/qdrant_client.py
"""Qdrant vector database client for semantic search."""

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import os

class QdrantClientWrapper:
    """Async wrapper for Qdrant vector database operations."""

    def __init__(self):
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_content")
        self.client: AsyncQdrantClient | None = None

    async def connect(self):
        """Initialize Qdrant client connection."""
        if not self.client:
            self.client = AsyncQdrantClient(
                url=self.url,
                api_key=self.api_key,
            )
        return self.client

    async def close(self):
        """Close Qdrant client connection."""
        if self.client:
            await self.client.close()
            self.client = None

    async def upsert_points(self, points: List[PointStruct]):
        """Insert or update vectors in collection."""
        client = await self.connect()
        return await client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        client = await self.connect()
        results = await client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        return results

# Global instance
qdrant_client = QdrantClientWrapper()
