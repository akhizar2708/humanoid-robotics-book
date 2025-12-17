# backend/src/services/ingestion.py
"""Document ingestion: MDX parsing, chunking, embedding, and storage."""

from typing import List, Dict, Any, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct
import hashlib
import re
import uuid

from .embedder import embed_chunks_batch
from ..db.qdrant_client import qdrant_client
from ..db.postgres_client import postgres_client


def parse_mdx(content: str) -> str:
    """
    Parse MDX content and extract plain text.

    Args:
        content: Raw MDX file content

    Returns:
        Plain text with frontmatter removed
    """
    # Remove frontmatter (YAML between ---)
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)

    # Remove JSX/React components (basic removal)
    content = re.sub(r'<[A-Z][^>]*>.*?</[A-Z][^>]*>', '', content, flags=re.DOTALL)
    content = re.sub(r'<[A-Z][^>]*\s*/>', '', content)

    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

    return content.strip()


def chunk_text(text: str, chunk_size: int = 1024, chunk_overlap: int = 128) -> List[str]:
    """
    Split text into chunks using RecursiveCharacterTextSplitter.

    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens (approximately)
        chunk_overlap: Overlap between chunks in tokens

    Returns:
        List of text chunks
    """
    # RecursiveCharacterTextSplitter with Markdown-aware separators
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size * 4,  # Approximate characters (4 chars ~ 1 token)
        chunk_overlap=chunk_overlap * 4,
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_text(text)
    return chunks


def has_code_block(text: str) -> bool:
    """Check if text contains code blocks (```...```)."""
    return bool(re.search(r'```[\s\S]*?```', text))


def get_heading_level(text: str) -> int:
    """Extract the highest heading level in text (1-6, or 0 if no headings)."""
    match = re.search(r'^(#{1,6})\s', text, re.MULTILINE)
    if match:
        return len(match.group(1))
    return 0


async def ingest_file(
    file_path: str,
    content: str,
    module_id: str,
    chapter_id: str,
    section_title: str,
    page_url: str | None = None
) -> Tuple[int, int]:
    """
    Ingest a single file: parse, chunk, embed, and store.

    Args:
        file_path: Relative file path (e.g., "docs/module-1/chapter-1.md")
        content: Full MDX file content
        module_id: Module identifier
        chapter_id: Chapter identifier
        section_title: Section title
        page_url: Docusaurus page URL (auto-generated if None)

    Returns:
        Tuple of (chunks_created, embeddings_generated)
    """
    # Auto-generate page URL if not provided
    if not page_url:
        page_url = f"/{module_id}/{chapter_id}"

    # Parse MDX
    plain_text = parse_mdx(content)

    # Chunk text
    chunks = chunk_text(plain_text)

    if not chunks:
        return 0, 0

    # Check for duplicates using content hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()

    existing = await postgres_client.fetchrow(
        "SELECT id FROM book_content WHERE content_hash = $1 LIMIT 1",
        content_hash
    )

    if existing:
        # Content unchanged, skip
        return 0, 0

    # Generate embeddings (batched)
    embeddings = await embed_chunks_batch(chunks, batch_size=20)

    # Prepare Qdrant points and Postgres records
    qdrant_points = []
    postgres_records = []

    for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
        chunk_id = str(uuid.uuid4())

        # Qdrant point
        qdrant_points.append(PointStruct(
            id=chunk_id,
            vector=embedding,
            payload={
                "module_id": module_id,
                "chapter_id": chapter_id,
                "section_title": section_title,
                "content_text": chunk_text,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "page_url": page_url,
                "contains_code": has_code_block(chunk_text),
                "heading_level": get_heading_level(chunk_text),
            }
        ))

        # Postgres record
        postgres_records.append({
            "id": chunk_id,
            "module_id": module_id,
            "chapter_id": chapter_id,
            "section_title": section_title,
            "content_text": chunk_text,
            "content_hash": hashlib.sha256(chunk_text.encode()).hexdigest(),
            "chunk_index": i,
            "total_chunks": len(chunks),
            "page_url": page_url,
            "contains_code": has_code_block(chunk_text),
            "heading_level": get_heading_level(chunk_text),
        })

    # Store in Qdrant
    await qdrant_client.upsert_points(qdrant_points)

    # Store in Postgres
    for record in postgres_records:
        await postgres_client.execute(
            """
            INSERT INTO book_content (
                id, module_id, chapter_id, section_title, content_text,
                content_hash, chunk_index, total_chunks, page_url,
                heading_level, contains_code
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (id) DO NOTHING
            """,
            record["id"], record["module_id"], record["chapter_id"],
            record["section_title"], record["content_text"],
            record["content_hash"], record["chunk_index"],
            record["total_chunks"], record["page_url"],
            record["heading_level"], record["contains_code"]
        )

    return len(chunks), len(embeddings)
