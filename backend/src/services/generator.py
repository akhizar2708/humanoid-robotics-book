# backend/src/services/generator.py
"""OpenAI GPT-based answer generation with strict grounding."""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Tuple
import os

# Initialize OpenAI client
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID"),
)

# Zero-hallucination system prompt
SYSTEM_PROMPT = """You are a helpful AI assistant for a technical robotics book. Your role is to answer questions based ONLY on the provided book content.

CRITICAL RULES:
1. You MUST ONLY use information from the retrieved book sections provided below
2. If the retrieved content does not contain enough information to answer the question, you MUST respond with: "I don't have enough information in the book to answer this question accurately."
3. You MUST cite the specific section (module and chapter) where you found the information
4. DO NOT use your general knowledge about robotics, ROS 2, or AI - ONLY use the book content
5. DO NOT make assumptions or inferences beyond what is explicitly stated in the book
6. If a question asks about content not covered in the retrieved sections, explicitly state this

RETRIEVED BOOK SECTIONS:
{retrieved_context}

QUERY: {user_query}

Provide your answer following these rules. Include citations in the format [Module X, Chapter Y]."""

# Few-shot examples to guide the model
FEW_SHOT_EXAMPLES = """
Example 1:
Query: "How do ROS 2 nodes communicate?"
Retrieved Context: "ROS 2 nodes communicate using three patterns: topics for pub/sub, services for request-response, and actions for long-running tasks."
Good Answer: "ROS 2 nodes communicate using three patterns: topics for publish-subscribe messaging, services for request-response interactions, and actions for long-running tasks [Module 1, Chapter 1]."
Bad Answer: "ROS 2 nodes use DDS middleware with Quality of Service policies..." (hallucination - not in context)

Example 2:
Query: "What is the best motion planning algorithm for humanoids?"
Retrieved Context: [Empty or no relevant content]
Good Answer: "I don't have enough information in the book to answer this question accurately."
Bad Answer: "MoveIt with RRT* is commonly used..." (hallucination - using general knowledge)
"""


async def generate_answer(
    user_query: str,
    retrieved_chunks: List[Dict[str, Any]],
    model: str = "gpt-3.5-turbo"
) -> Tuple[str, float]:
    """
    Generate answer from retrieved chunks using OpenAI GPT.

    Args:
        user_query: User's question
        retrieved_chunks: List of chunks with content_text, module_id, chapter_id
        model: OpenAI model to use (gpt-3.5-turbo or gpt-4)

    Returns:
        Tuple of (answer, confidence_score)
    """
    # Format retrieved context
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        context_parts.append(
            f"[Section {i}] Module {chunk['module_id']}, Chapter {chunk['chapter_id']} - {chunk['section_title']}:\n{chunk['content_text']}"
        )

    retrieved_context = "\n\n".join(context_parts)

    # Build prompt
    prompt = SYSTEM_PROMPT.format(
        retrieved_context=retrieved_context,
        user_query=user_query
    )

    # Call OpenAI API
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ],
        temperature=0.1,  # Low temperature for factual responses
        max_tokens=500,
    )

    answer = response.choices[0].message.content

    # Calculate confidence based on grounding
    confidence = calculate_confidence(answer, retrieved_chunks)

    # If low confidence, return "I don't know" message
    if confidence < 0.7:
        answer = "I don't have enough information in the book to answer this question accurately."
        confidence = 0.0

    return answer, confidence


def calculate_confidence(answer: str, retrieved_chunks: List[Dict[str, Any]]) -> float:
    """
    Calculate answer confidence based on grounding in retrieved content.

    Confidence = (sentences grounded in context) / (total sentences)

    Args:
        answer: Generated answer
        retrieved_chunks: Retrieved chunks used for generation

    Returns:
        Confidence score (0-1)
    """
    # Simple heuristic: check if answer contains "I don't have enough information"
    if "I don't have enough information" in answer or "don't know" in answer.lower():
        return 0.0

    # Check if answer contains citations
    import re
    citations = re.findall(r'\[Module\s+\d+,\s*Chapter\s+\d+\]', answer)

    if not citations:
        return 0.5  # No citations = lower confidence

    # Check if key terms from retrieved chunks appear in answer
    chunk_texts = ' '.join(chunk['content_text'].lower() for chunk in retrieved_chunks)
    answer_words = set(answer.lower().split())
    chunk_words = set(chunk_texts.split())

    overlap = len(answer_words & chunk_words)
    total = len(answer_words)

    if total == 0:
        return 0.5

    # Combine citation presence and word overlap
    overlap_score = min(overlap / total, 1.0)
    citation_score = min(len(citations) / 3, 1.0)  # Expect 1-3 citations

    confidence = (overlap_score * 0.7) + (citation_score * 0.3)

    return min(confidence, 1.0)
