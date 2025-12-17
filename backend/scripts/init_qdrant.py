# backend/scripts/init_qdrant.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, ScalarQuantization
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def init_qdrant_collection():
    """Initialize Qdrant collection for book content embeddings."""
    client = AsyncQdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
    )

    # Create collection if not exists
    collections = await client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if "book_content" not in collection_names:
        await client.create_collection(
            collection_name="book_content",
            vectors_config=VectorParams(
                size=1536,  # OpenAI text-embedding-3-small dimension
                distance=Distance.COSINE,
            ),
        )
        print("✓ Created collection 'book_content'")

        # Add quantization for storage optimization
        await client.update_collection(
            collection_name="book_content",
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantization.ScalarType.INT8,
                quantile=0.99,
                always_ram=True,
            ),
        )
        print("✓ Enabled int8 quantization")
    else:
        print("✓ Collection 'book_content' already exists")

    await client.close()

if __name__ == "__main__":
    asyncio.run(init_qdrant_collection())
