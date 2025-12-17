# API Contracts Overview

**Feature**: 001-docusaurus-infrastructure
**Created**: 2025-12-16
**Status**: Complete

This directory contains OpenAPI 3.0 specifications for all backend API endpoints.

## Available Contracts

### 1. RAG Query API (`rag-api.yaml`)

**Purpose**: Handles user queries and returns AI-generated answers grounded in book content

**Endpoint**: `POST /api/v1/query`

**Key Features**:
- Supports global and selected-text query modes
- Returns answer with section-level citations
- Includes confidence scoring
- Provides retrieved chunk details for transparency

**Use Cases**:
- User asks question about book content
- User selects text and asks for clarification
- Chatbot widget sends queries from Docusaurus frontend

---

### 2. Document Ingestion API (`embedding-api.yaml`)

**Purpose**: Ingests MDX book content, generates embeddings, and stores in vector database

**Endpoint**: `POST /api/v1/ingest`

**Key Features**:
- Batch processing of multiple documents
- Automatic chunking and embedding generation
- Duplicate detection via content hashing
- Progress reporting for large ingestion jobs

**Use Cases**:
- Initial book content ingestion
- Updating content after edits
- Adding new modules or chapters
- CI/CD automated content synchronization

---

## Authentication

**Current**: No authentication (public book, free access)

**Future**: API key authentication for ingestion endpoint to prevent abuse

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

---

## CORS Configuration

FastAPI backend must allow requests from:
- `http://localhost:3000` (local Docusaurus dev server)
- `https://your-username.github.io` (deployed GitHub Pages site)

```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-username.github.io",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Error Handling

All endpoints follow consistent error response format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Query text is required",
    "details": {
      "field": "query",
      "constraint": "minLength:1"
    }
  }
}
```

**Standard Error Codes**:
- `400` - Invalid request (missing fields, validation errors)
- `429` - Rate limit exceeded (OpenAI API limits)
- `500` - Internal server error (database, API failures)
- `503` - Service unavailable (maintenance mode)

---

## Rate Limiting

**OpenAI API Limits** (tier-dependent):
- Tier 1: 3 RPM (requests per minute) for embeddings
- Tier 2: 60 RPM for embeddings

**Backend Rate Limiting** (implemented via middleware):
- Query endpoint: 10 requests/minute per session
- Ingestion endpoint: 5 requests/hour (prevents abuse)

---

## Testing

### Query API Test

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "query_scope": "global",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "top_k": 5
  }'
```

### Ingestion API Test

```bash
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content_files": [
      {
        "file_path": "docs/module-1/chapter-1.md",
        "content": "# ROS 2 Fundamentals\n\nROS 2 is...",
        "metadata": {
          "module_id": "module-1",
          "chapter_id": "chapter-1",
          "section_title": "ROS 2 Fundamentals"
        }
      }
    ]
  }'
```

---

## Contract Validation

Use OpenAPI validators to ensure implementation matches contracts:

```bash
# Install validator
pip install openapi-spec-validator

# Validate contracts
openapi-spec-validator contracts/rag-api.yaml
openapi-spec-validator contracts/embedding-api.yaml
```

---

## Next Steps

1. Review individual contract files (`rag-api.yaml`, `embedding-api.yaml`)
2. Generate API client code (optional): `openapi-generator-cli generate`
3. Implement FastAPI endpoints matching these contracts
4. Write contract tests to validate implementation
