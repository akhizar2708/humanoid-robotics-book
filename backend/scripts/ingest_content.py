#!/usr/bin/env python3
# backend/scripts/ingest_content.py
"""CLI script to ingest book content from docs/ directory."""

import asyncio
import argparse
import os
import sys
from pathlib import Path
import httpx
import json

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()


async def ingest_directory(docs_dir: str, api_url: str = "http://localhost:8000"):
    """
    Scan docs directory and ingest all .md files.

    Args:
        docs_dir: Path to docs/ directory (e.g., "../book/docs")
        api_url: Backend API URL
    """
    docs_path = Path(docs_dir)

    if not docs_path.exists():
        print(f"Error: Directory not found: {docs_dir}")
        return

    print(f"[INFO] Scanning docs directory: {docs_path}")

    # Find all .md files
    md_files = list(docs_path.rglob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith("_")]  # Exclude _category_.json etc.

    print(f"[INFO] Found {len(md_files)} markdown files")

    if not md_files:
        print("[WARNING] No markdown files found")
        return

    # Process files and group by module
    content_files = []

    for md_file in md_files:
        # Parse file path to extract module and chapter
        relative_path = md_file.relative_to(docs_path)
        parts = relative_path.parts

        if len(parts) < 2:
            print(f"[SKIP] {md_file}: Not in module/chapter structure")
            continue

        module_id = parts[0]  # e.g., "module-1"
        chapter_file = parts[1]  # e.g., "chapter-1.md"
        chapter_id = chapter_file.replace(".md", "")  # e.g., "chapter-1"

        # Read file content
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from frontmatter or first heading
        section_title = extract_title(content, chapter_id)

        content_files.append({
            "file_path": str(relative_path),
            "content": content,
            "metadata": {
                "module_id": module_id,
                "chapter_id": chapter_id,
                "section_title": section_title,
                "page_url": f"/{module_id}/{chapter_id}"
            }
        })

        print(f"  ✓ Prepared: {module_id}/{chapter_id} - {section_title}")

    if not content_files:
        print("[ERROR] No valid content files to ingest")
        return

    # Send to ingestion API (batch by 10 files to avoid large requests)
    batch_size = 10
    total_chunks = 0
    total_embeddings = 0
    total_errors = 0

    async with httpx.AsyncClient(timeout=300.0) as client:
        for i in range(0, len(content_files), batch_size):
            batch = content_files[i:i + batch_size]

            print(f"\n[INFO] Ingesting batch {i//batch_size + 1} ({len(batch)} files)...")

            try:
                response = await client.post(
                    f"{api_url}/api/v1/ingest",
                    json={"content_files": batch}
                )

                if response.status_code == 200:
                    result = response.json()
                    total_chunks += result["chunks_created"]
                    total_embeddings += result["embeddings_generated"]

                    print(f"  ✓ Chunks created: {result['chunks_created']}")
                    print(f"  ✓ Embeddings generated: {result['embeddings_generated']}")
                    print(f"  ✓ Status: {result['status']}")

                    if result.get("errors"):
                        total_errors += len(result["errors"])
                        for error in result["errors"]:
                            print(f"  ✗ Error in {error['file_path']}: {error['message']}")
                else:
                    print(f"  ✗ API error: {response.status_code}")
                    print(f"     {response.text}")
                    total_errors += len(batch)

            except Exception as e:
                print(f"  ✗ Request failed: {e}")
                total_errors += len(batch)

    print(f"\n[SUCCESS] Ingestion complete")
    print(f"  - Total files processed: {len(content_files)}")
    print(f"  - Chunks created: {total_chunks}")
    print(f"  - Embeddings generated: {total_embeddings}")
    print(f"  - Errors: {total_errors}")


def extract_title(content: str, fallback: str) -> str:
    """Extract title from MDX frontmatter or first heading."""
    import re

    # Try frontmatter
    frontmatter_match = re.search(r'^---\s*\ntitle:\s*["\']?(.+?)["\']?\s*\n', content, re.MULTILINE)
    if frontmatter_match:
        return frontmatter_match.group(1)

    # Try first H1 heading
    heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if heading_match:
        return heading_match.group(1)

    # Fallback to chapter ID
    return fallback.replace("-", " ").title()


def main():
    parser = argparse.ArgumentParser(description="Ingest book content into RAG system")
    parser.add_argument(
        "--docs-dir",
        default="../book/docs",
        help="Path to docs directory (default: ../book/docs)"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="Backend API URL (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    asyncio.run(ingest_directory(args.docs_dir, args.api_url))


if __name__ == "__main__":
    main()
