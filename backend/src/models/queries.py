# backend/src/models/queries.py
"""Pydantic models for RAG queries."""

from pydantic import BaseModel, Field, UUID4
from typing import List, Literal

class QueryRequest(BaseModel):
    """Request to query book content with RAG."""
    query: str = Field(..., min_length=1, max_length=1000, description="User's question")
    query_scope: Literal["global", "selected"] = Field(..., description="Query scope (entire book or selected text)")
    selected_text: str | None = Field(None, min_length=10, max_length=5000, description="Selected text (required if query_scope='selected')")
    session_id: UUID4 = Field(..., description="Chat session identifier")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve")

class Citation(BaseModel):
    """Section-level citation."""
    section_title: str
    module_id: str
    chapter_id: str
    page_url: str

class RetrievedChunk(BaseModel):
    """Retrieved chunk with relevance score."""
    chunk_id: str
    score: float = Field(..., ge=0, le=1, description="Cosine similarity score (0-1)")
    content_preview: str = Field(..., description="First 200 characters of chunk")

class QueryResponse(BaseModel):
    """Response from RAG query."""
    answer: str = Field(..., description="Generated answer or 'I don't have enough information...'")
    citations: List[Citation] = Field(default_factory=list)
    retrieved_chunks: List[RetrievedChunk] = Field(default_factory=list)
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence score (0-1)")

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: dict = Field(..., description="Error details with code, message, and optional details")
