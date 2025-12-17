# Backend API - AI-Driven Humanoid Robotics

FastAPI-based backend providing RAG (Retrieval-Augmented Generation) chatbot capabilities for the AI-Driven Humanoid Robotics technical book.

## Overview

This backend implements:
- Document ingestion and embedding pipeline
- RAG query endpoint with citation extraction
- Vector similarity search (Qdrant)
- Conversation tracking (PostgreSQL)
- Rate limiting and CORS middleware

## Tech Stack

- **FastAPI** 0.109+ - Async Python web framework
- **LangChain** 0.1+ - RAG orchestration
- **OpenAI API** - Embeddings (text-embedding-3-small) and generation (GPT-3.5-turbo)
- **Qdrant** - Vector database for semantic search
- **PostgreSQL** (Neon) - Metadata and conversation logs
- **Pydantic** - Data validation and settings management

## Setup

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment tool (venv)
- OpenAI API key
- Qdrant Cloud account (free tier)
- Neon Postgres account (free tier)

### Installation

```bash
# 1. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_EMBED=text-embedding-3-small
OPENAI_MODEL_CHAT=gpt-3.5-turbo

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION=humanoid_robotics_book

# PostgreSQL Configuration (Neon)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://your-username.github.io

# Rate Limiting
RATE_LIMIT_QUERIES_PER_MINUTE=10
RATE_LIMIT_INGESTIONS_PER_HOUR=5
```

See `.env.example` for a complete template.

### Database Initialization

```bash
# 1. Initialize Qdrant collection
python scripts/init_qdrant.py

# 2. Initialize PostgreSQL schema
# Using psql:
psql $DATABASE_URL -f scripts/init_postgres.sql

# Or using Neon SQL Editor:
# Copy/paste contents of scripts/init_postgres.sql
```

## Running the Server

### Development Mode

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns server status and database connectivity.

### Document Ingestion

```http
POST /api/v1/ingest
Content-Type: application/json

{
  "files": [
    {
      "path": "module-1/chapter-1.md",
      "content": "# Chapter 1...",
      "metadata": {
        "module": "Module 1",
        "chapter": "Chapter 1",
        "title": "Introduction to ROS 2"
      }
    }
  ]
}
```

Ingests book content, chunks it, generates embeddings, and stores in Qdrant + Postgres.

### Ingestion Status

```http
GET /api/v1/ingest/status
```

Returns ingestion statistics (total chunks, last update time).

### RAG Query

```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "What is ROS 2?",
  "session_id": "session_123",
  "query_scope": "global"
}
```

Or with selected text:

```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "Explain this in more detail",
  "session_id": "session_123",
  "query_scope": "selected",
  "selected_text": "ROS 2 uses DDS middleware..."
}
```

Returns AI-generated answer with citations.

## Project Structure

```
backend/
├── src/
│   ├── api/              # FastAPI route handlers
│   │   ├── __init__.py
│   │   ├── ingest.py     # POST /api/v1/ingest
│   │   └── rag.py        # POST /api/v1/query
│   ├── db/               # Database clients
│   │   ├── __init__.py
│   │   ├── qdrant_client.py
│   │   └── postgres_client.py
│   ├── models/           # Pydantic models
│   │   ├── __init__.py
│   │   ├── documents.py  # ContentFile, ContentMetadata
│   │   ├── embeddings.py # IngestRequest, IngestResponse
│   │   └── queries.py    # QueryRequest, QueryResponse
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   ├── embedder.py   # OpenAI embeddings
│   │   ├── retriever.py  # Qdrant similarity search
│   │   ├── generator.py  # GPT response generation
│   │   ├── citation_extractor.py
│   │   └── ingestion.py  # MDX parsing and chunking
│   ├── config.py         # Environment variable configuration
│   └── main.py           # FastAPI app initialization
├── scripts/
│   ├── init_qdrant.py    # Initialize Qdrant collection
│   ├── init_postgres.sql # PostgreSQL schema
│   └── ingest_content.py # CLI for bulk ingestion
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── .env.example          # Environment variable template
└── README.md             # This file
```

## Ingesting Book Content

Use the CLI script to ingest all book chapters:

```bash
python scripts/ingest_content.py --docs-dir ../book/docs
```

Options:
- `--docs-dir`: Path to Docusaurus docs directory (default: `../book/docs`)
- `--api-url`: Backend API URL (default: `http://localhost:8000`)

## Development

### Code Formatting

```bash
black src/ scripts/
```

### Linting

```bash
flake8 src/ scripts/
```

### Type Checking

```bash
mypy src/
```

### Running Tests

```bash
pytest tests/ -v
```

### Test Coverage

```bash
pytest tests/ --cov=src --cov-report=html
```

## Architecture

### RAG Pipeline

1. **Ingestion**:
   - Parse MDX files → Extract frontmatter metadata
   - Chunk text (1024 tokens, 128 overlap)
   - Generate embeddings (text-embedding-3-small)
   - Store in Qdrant (vectors) + Postgres (metadata)

2. **Query**:
   - Embed user query → Similarity search in Qdrant
   - Retrieve top-k chunks → Construct prompt
   - Generate answer with GPT-3.5-turbo
   - Extract citations → Log to Postgres

### Database Schema

**Qdrant Collection**: `humanoid_robotics_book`
- Vector size: 1536 (text-embedding-3-small)
- Distance: Cosine
- Quantization: int8 (4x compression)
- Payload: `{module, chapter, title, content, chunk_index}`

**PostgreSQL Tables**:
- `book_content`: Ingested chunks with metadata
- `chat_session`: User chat sessions
- `chat_message`: Individual messages
- `retrieval_log`: Query logs with retrieved chunks

See [data-model.md](../specs/001-docusaurus-infrastructure/data-model.md) for full schema.

## Performance

- **Embedding cache**: 1-hour TTL, 1000 entry max
- **Rate limiting**: 10 queries/min per session, 5 ingestions/hour
- **Chunk retrieval**: Top-10 chunks per query
- **Response time**: <2s for typical queries

## Security

- API key validation for all OpenAI requests
- Input sanitization on all endpoints
- CORS restricted to allowed origins
- Rate limiting to prevent abuse
- No secrets in version control

## Deployment

See [quickstart.md](../specs/001-docusaurus-infrastructure/quickstart.md) for deployment guides:
- Render.com (recommended, free tier)
- Railway.app (alternative)
- Fly.io (alternative)

## Troubleshooting

### "Connection refused" errors

Ensure Qdrant and Postgres are accessible:

```bash
python scripts/init_qdrant.py  # Should connect without errors
psql $DATABASE_URL -c "SELECT 1"  # Should return 1
```

### "API key not valid" errors

Check your OpenAI API key:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Slow query responses

1. Check Qdrant collection size: `GET /collections/humanoid_robotics_book`
2. Verify embedding cache is working (check logs for cache hits)
3. Consider upgrading to GPT-4 for higher quality (slower)

## API Documentation

Interactive API documentation available when server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Contributing

1. Create a feature branch
2. Make changes with tests
3. Run `black` and `flake8`
4. Submit PR with description

## License

MIT License - see [../LICENSE](../LICENSE)
