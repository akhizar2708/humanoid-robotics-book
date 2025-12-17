# backend/src/models/documents.py
"""Pydantic models for document ingestion."""

from pydantic import BaseModel, Field
from typing import List

class ContentMetadata(BaseModel):
    """Metadata for book content."""
    module_id: str = Field(..., pattern=r'^module-[1-9]\d*$', description="Module identifier (e.g., 'module-1')")
    chapter_id: str = Field(..., pattern=r'^chapter-[1-9]\d*$', description="Chapter identifier (e.g., 'chapter-1')")
    section_title: str = Field(..., min_length=1, max_length=255, description="Section/chapter title")
    page_url: str | None = Field(None, description="Docusaurus page URL (auto-generated if not provided)")

class ContentFile(BaseModel):
    """Individual content file for ingestion."""
    file_path: str = Field(..., description="Relative path to MDX file (e.g., 'docs/module-1/chapter-1.md')")
    content: str = Field(..., min_length=100, max_length=100000, description="Full MDX file content")
    metadata: ContentMetadata

class IngestRequest(BaseModel):
    """Request to ingest book content."""
    content_files: List[ContentFile] = Field(..., min_length=1, max_length=50, description="Array of content files (max 50 per request)")

class IngestError(BaseModel):
    """Error for a file that failed to process."""
    file_path: str
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = None

class IngestResponse(BaseModel):
    """Response from content ingestion."""
    chunks_created: int = Field(..., ge=0)
    embeddings_generated: int = Field(..., ge=0)
    skipped_unchanged: int = Field(..., ge=0)
    status: str = Field(..., description="success, partial, or failed")
    processing_time_ms: int = Field(..., ge=0)
    errors: List[IngestError] = Field(default_factory=list)

class ModuleStats(BaseModel):
    """Statistics for a single module."""
    module_id: str
    chunk_count: int
    last_updated: str  # ISO 8601 timestamp

class StorageUsage(BaseModel):
    """Storage usage statistics."""
    qdrant_mb: float
    postgres_mb: float

class IngestionStatus(BaseModel):
    """Overall ingestion status."""
    total_chunks: int = Field(..., ge=0)
    total_embeddings: int = Field(..., ge=0)
    modules: List[ModuleStats]
    storage_usage: StorageUsage
    last_ingestion: str  # ISO 8601 timestamp
