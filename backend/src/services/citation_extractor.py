# backend/src/services/citation_extractor.py
"""Extract citations from generated answers."""

import re
from typing import List, Dict, Any
from ..db.postgres_client import postgres_client


async def extract_citations(answer: str) -> List[Dict[str, str]]:
    """
    Extract [Module X, Chapter Y] citations from generated answer.

    Args:
        answer: Generated answer text

    Returns:
        List of citation dictionaries with module_id, chapter_id, section_title, page_url
    """
    # Pattern: [Module 1, Chapter 2] or [Module 1, Ch 2]
    pattern = r'\[Module\s+(\d+),\s*(?:Chapter|Ch)\s+(\d+)\]'
    matches = re.findall(pattern, answer, re.IGNORECASE)

    citations = []
    seen = set()  # Avoid duplicate citations

    for module_num, chapter_num in matches:
        module_id = f"module-{module_num}"
        chapter_id = f"chapter-{chapter_num}"

        # Skip if already added
        citation_key = (module_id, chapter_id)
        if citation_key in seen:
            continue

        seen.add(citation_key)

        # Lookup section title from database
        section_title = await get_section_title(module_id, chapter_id)

        citations.append({
            "module_id": module_id,
            "chapter_id": chapter_id,
            "section_title": section_title,
            "page_url": f"/{module_id}/{chapter_id}",
        })

    return citations


async def get_section_title(module_id: str, chapter_id: str) -> str:
    """
    Retrieve section title from database.

    Args:
        module_id: Module identifier (e.g., "module-1")
        chapter_id: Chapter identifier (e.g., "chapter-1")

    Returns:
        Section title or "Unknown Section" if not found
    """
    query = """
        SELECT DISTINCT section_title
        FROM book_content
        WHERE module_id = $1 AND chapter_id = $2
        LIMIT 1
    """

    result = await postgres_client.fetchrow(query, module_id, chapter_id)

    if result and result.get("section_title"):
        return result["section_title"]

    # Fallback to formatted module/chapter name
    return f"{module_id.replace('-', ' ').title()}, {chapter_id.replace('-', ' ').title()}"
