# Data Model: Docusaurus Infrastructure + RAG Chatbot

**Feature**: 001-docusaurus-infrastructure
**Created**: 2025-12-16
**Status**: Complete
**Prerequisites**: research.md

This document defines all data entities, schemas, and database configurations for the book platform and RAG chatbot.

---

## Overview

The system uses two database types:
- **Qdrant Cloud** (Vector Database): Stores document embeddings for semantic search
- **Neon Serverless Postgres** (Relational Database): Stores metadata, chat history, and analytics

---

## 1. BookContent Entity

**Purpose**: Represents chunked book content with embeddings for RAG retrieval

**Storage**: Qdrant (vectors) + Postgres (metadata)

### Qdrant Collection Schema

```python
# Collection: book_content
# Vector Configuration
{
    "vectors": {
        "size": 1536,              # OpenAI text-embedding-3-small dimension
        "distance": "Cosine",      # Cosine similarity for semantic search
    },
    "quantization_config": {
        "scalar": {
            "type": "int8",        # Quantization for storage optimization
            "quantile": 0.99,
            "always_ram": True,
        }
    }
}

# Payload Schema (metadata stored with each vector)
{
    "id": "uuid",                  # Unique chunk identifier
    "module_id": "string",         # e.g., "module-1"
    "chapter_id": "string",        # e.g., "chapter-1"
    "section_title": "string",     # Section heading
    "content_text": "string",      # Raw text (1024 tokens max)
    "chunk_index": "integer",      # Position in document (0-based)
    "total_chunks": "integer",     # Total chunks in document
    "page_url": "string",          # Docusaurus page URL
    "heading_level": "integer",    # Markdown heading level (1-6)
    "contains_code": "boolean",    # Has code blocks
    "created_at": "timestamp",     # Ingestion timestamp
}
```

### Postgres Table Schema

```sql
CREATE TABLE book_content (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id VARCHAR(50) NOT NULL,
    chapter_id VARCHAR(50) NOT NULL,
    section_title VARCHAR(255) NOT NULL,
    content_text TEXT NOT NULL CHECK (char_length(content_text) BETWEEN 100 AND 10000),
    content_hash VARCHAR(64) NOT NULL,  -- SHA-256 hash for change detection
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    total_chunks INTEGER NOT NULL CHECK (total_chunks > 0),
    page_url VARCHAR(255) NOT NULL,
    heading_level INTEGER CHECK (heading_level BETWEEN 1 AND 6),
    contains_code BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_chunk UNIQUE (module_id, chapter_id, chunk_index),
    CONSTRAINT valid_chunk_index CHECK (chunk_index < total_chunks)
);

-- Indexes for fast lookup
CREATE INDEX idx_book_content_module ON book_content(module_id);
CREATE INDEX idx_book_content_chapter ON book_content(chapter_id);
CREATE INDEX idx_book_content_hash ON book_content(content_hash);
CREATE INDEX idx_book_content_created ON book_content(created_at DESC);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_content_updated_at
    BEFORE UPDATE ON book_content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Validation Rules

- `content_text`: 100-10,000 characters (approximately 25-2500 tokens)
- `chunk_index`: Must be < `total_chunks`
- `content_hash`: SHA-256 of content for change detection
- `module_id` and `chapter_id`: Match Docusaurus directory structure

### Relationships

- Belongs to Module (logical grouping, not FK)
- Belongs to Chapter (logical grouping, not FK)
- Has many RetrievalLog entries (via chunk_id references)

---

## 2. ChatSession Entity

**Purpose**: Represents a user's chat session with conversation history

**Storage**: Postgres only

### Postgres Table Schema

```sql
CREATE TABLE chat_session (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),              -- Optional: future user auth
    user_agent TEXT,                   -- Browser/client info
    ip_address INET,                   -- Client IP (hashed for privacy)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0 CHECK (message_count >= 0),
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT valid_timestamps CHECK (last_active >= created_at)
);

-- Indexes
CREATE INDEX idx_chat_session_user ON chat_session(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_chat_session_active ON chat_session(is_active, last_active DESC);
CREATE INDEX idx_chat_session_created ON chat_session(created_at DESC);

-- Automatic session expiration (90 days inactive)
CREATE INDEX idx_chat_session_expire ON chat_session(last_active)
    WHERE is_active = TRUE AND last_active < CURRENT_TIMESTAMP - INTERVAL '90 days';
```

### Validation Rules

- `last_active` >= `created_at`
- `message_count` >= 0
- Auto-expire sessions inactive for 90 days

### Relationships

- Has many ChatMessage entries (one-to-many)

---

## 3. ChatMessage Entity

**Purpose**: Stores individual messages (user queries and assistant responses)

**Storage**: Postgres only

### Postgres Table Schema

```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE query_scope AS ENUM ('global', 'selected');

CREATE TABLE chat_message (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_session(session_id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL CHECK (char_length(content) BETWEEN 1 AND 10000),

    -- User message fields
    query_scope query_scope,           -- Required for role='user'
    selected_text TEXT,                -- Required when query_scope='selected'

    -- Assistant message fields
    retrieved_chunks JSONB,            -- Array of chunk IDs used
    confidence DECIMAL(3,2) CHECK (confidence BETWEEN 0 AND 1),

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT user_message_scope CHECK (
        (role != 'user') OR (query_scope IS NOT NULL)
    ),
    CONSTRAINT selected_text_required CHECK (
        (role != 'user') OR (query_scope != 'selected') OR (selected_text IS NOT NULL)
    ),
    CONSTRAINT assistant_metadata CHECK (
        (role != 'assistant') OR (retrieved_chunks IS NOT NULL AND confidence IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_chat_message_session ON chat_message(session_id, timestamp DESC);
CREATE INDEX idx_chat_message_role ON chat_message(role);
CREATE INDEX idx_chat_message_timestamp ON chat_message(timestamp DESC);

-- GIN index for JSONB queries
CREATE INDEX idx_chat_message_chunks ON chat_message USING GIN (retrieved_chunks);

-- Update session last_active on new message
CREATE OR REPLACE FUNCTION update_session_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_session
    SET last_active = NEW.timestamp,
        message_count = message_count + 1
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_session_activity
    AFTER INSERT ON chat_message
    FOR EACH ROW
    EXECUTE FUNCTION update_session_on_message();
```

### Example JSONB Structure for `retrieved_chunks`

```json
{
  "chunks": [
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
      "module_id": "module-1",
      "chapter_id": "chapter-1",
      "section_title": "ROS 2 Architecture",
      "score": 0.89,
      "rank": 1
    },
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440001",
      "module_id": "module-1",
      "chapter_id": "chapter-1",
      "section_title": "DDS Middleware",
      "score": 0.82,
      "rank": 2
    }
  ],
  "total_retrieved": 5,
  "used_count": 2
}
```

### Validation Rules

- User messages MUST have `query_scope`
- Selected-text queries MUST have `selected_text`
- Assistant messages MUST have `retrieved_chunks` and `confidence`
- `content`: 1-10,000 characters

### Relationships

- Belongs to ChatSession (many-to-one)
- References BookContent chunks via `retrieved_chunks` JSONB

---

## 4. RetrievalLog Entity

**Purpose**: Analytics and debugging for RAG retrieval quality

**Storage**: Postgres only

### Postgres Table Schema

```sql
CREATE TABLE retrieval_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_session(session_id) ON DELETE SET NULL,
    message_id UUID REFERENCES chat_message(message_id) ON DELETE SET NULL,

    query_text TEXT NOT NULL,
    query_embedding VECTOR(1536),      -- Requires pgvector extension

    top_k_requested INTEGER NOT NULL CHECK (top_k_requested BETWEEN 1 AND 20),
    top_k_results JSONB NOT NULL,      -- Array of {chunk_id, score} objects
    selected_chunks JSONB,              -- Chunks actually used in response

    query_scope query_scope NOT NULL,
    selected_text TEXT,

    retrieval_time_ms INTEGER CHECK (retrieval_time_ms >= 0),
    generation_time_ms INTEGER CHECK (generation_time_ms >= 0),
    total_time_ms INTEGER CHECK (total_time_ms >= 0),

    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_timing CHECK (total_time_ms >= retrieval_time_ms + generation_time_ms)
);

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Indexes
CREATE INDEX idx_retrieval_log_session ON retrieval_log(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX idx_retrieval_log_timestamp ON retrieval_log(timestamp DESC);
CREATE INDEX idx_retrieval_log_scope ON retrieval_log(query_scope);

-- GIN indexes for JSONB
CREATE INDEX idx_retrieval_log_results ON retrieval_log USING GIN (top_k_results);
CREATE INDEX idx_retrieval_log_selected ON retrieval_log USING GIN (selected_chunks);

-- Vector index for similarity search (debugging)
CREATE INDEX idx_retrieval_log_embedding ON retrieval_log
    USING ivfflat (query_embedding vector_cosine_ops)
    WITH (lists = 100);
```

### Example JSONB Structure for `top_k_results`

```json
[
  {
    "chunk_id": "550e8400-e29b-41d4-a716-446655440000",
    "score": 0.89,
    "rank": 1,
    "module_id": "module-1",
    "chapter_id": "chapter-1"
  },
  {
    "chunk_id": "550e8400-e29b-41d4-a716-446655440001",
    "score": 0.82,
    "rank": 2,
    "module_id": "module-1",
    "chapter_id": "chapter-2"
  }
]
```

### Validation Rules

- `top_k_requested`: 1-20
- `retrieval_time_ms` + `generation_time_ms` <= `total_time_ms`
- `query_embedding`: 1536 dimensions (OpenAI text-embedding-3-small)

### Relationships

- Belongs to ChatSession (optional, nullable)
- Belongs to ChatMessage (optional, nullable)
- References BookContent chunks via JSONB arrays

---

## 5. Database Initialization Scripts

### Qdrant Collection Setup

```python
# backend/scripts/init_qdrant.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, ScalarQuantization
import asyncio
import os

async def init_qdrant_collection():
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
                size=1536,
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
```

### Postgres Schema Setup

```sql
-- backend/scripts/init_postgres.sql

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE query_scope AS ENUM ('global', 'selected');

-- Create tables (in dependency order)
CREATE TABLE IF NOT EXISTS chat_session (
    -- [Full schema from section 2 above]
);

CREATE TABLE IF NOT EXISTS book_content (
    -- [Full schema from section 1 above]
);

CREATE TABLE IF NOT EXISTS chat_message (
    -- [Full schema from section 3 above]
);

CREATE TABLE IF NOT EXISTS retrieval_log (
    -- [Full schema from section 4 above]
);

-- Create indexes
-- [All indexes from above]

-- Create triggers
-- [All triggers from above]

-- Insert seed data (optional)
-- None needed for initial setup
```

---

## 6. Data Access Patterns

### Common Queries

**1. Retrieve all chunks for a module:**

```sql
SELECT id, chapter_id, section_title, content_text
FROM book_content
WHERE module_id = 'module-1'
ORDER BY chapter_id, chunk_index;
```

**2. Find session chat history:**

```sql
SELECT cm.role, cm.content, cm.timestamp, cm.confidence
FROM chat_message cm
WHERE cm.session_id = $1
ORDER BY cm.timestamp ASC;
```

**3. Get retrieval analytics (average scores by module):**

```sql
SELECT
    jsonb_array_elements(top_k_results)->>'module_id' AS module_id,
    AVG((jsonb_array_elements(top_k_results)->>'score')::DECIMAL) AS avg_score,
    COUNT(*) AS query_count
FROM retrieval_log
WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY module_id
ORDER BY avg_score DESC;
```

**4. Detect duplicate content (before ingestion):**

```sql
SELECT id, module_id, chapter_id, content_hash
FROM book_content
WHERE content_hash = $1;
```

---

## 7. Data Migration Strategy

### Version 1.0 → 1.1 (Future Schema Changes)

```sql
-- Example: Add language field for i18n
ALTER TABLE book_content
ADD COLUMN language VARCHAR(10) DEFAULT 'en' NOT NULL;

CREATE INDEX idx_book_content_language ON book_content(language);
```

### Backfill Strategy

```python
# backend/scripts/backfill_hashes.py
import hashlib
import asyncpg

async def backfill_content_hashes():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    rows = await conn.fetch("SELECT id, content_text FROM book_content WHERE content_hash IS NULL")

    for row in rows:
        content_hash = hashlib.sha256(row['content_text'].encode()).hexdigest()
        await conn.execute(
            "UPDATE book_content SET content_hash = $1 WHERE id = $2",
            content_hash, row['id']
        )

    await conn.close()
    print(f"✓ Backfilled {len(rows)} content hashes")
```

---

## 8. Storage Estimates

### Qdrant (Vectors)

- **4 modules** × 5 chapters × 200 sections = **1,000 chunks**
- **1,000 vectors** × 1536 dims × 4 bytes = **6.1 MB** raw
- With int8 quantization: **~1.5 MB** (75% reduction)
- **Free tier limit**: 1 GB (plenty of headroom)

### Neon Postgres (Metadata)

- **book_content**: 1,000 rows × 2 KB = **2 MB**
- **chat_session**: 1,000 sessions × 0.5 KB = **500 KB**
- **chat_message**: 10,000 messages × 1 KB = **10 MB**
- **retrieval_log**: 10,000 logs × 2 KB = **20 MB**
- **Total**: ~32 MB (fits in 512 MB free tier)

---

## Summary

| Entity | Qdrant | Postgres | Purpose |
|--------|--------|----------|---------|
| **BookContent** | ✓ (vectors) | ✓ (metadata) | Document chunks with embeddings |
| **ChatSession** | ✗ | ✓ | User conversation sessions |
| **ChatMessage** | ✗ | ✓ | Individual messages in chat |
| **RetrievalLog** | ✗ | ✓ | Analytics and debugging |

**Next Steps**:
1. Run `init_qdrant.py` to create Qdrant collection
2. Run `init_postgres.sql` to create Postgres schema
3. Proceed to API contract definition (contracts/)
