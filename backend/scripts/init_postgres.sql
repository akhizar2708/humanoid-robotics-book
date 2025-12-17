-- backend/scripts/init_postgres.sql
-- Complete database schema for RAG chatbot book platform

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE IF NOT EXISTS message_role AS ENUM ('user', 'assistant', 'system');
CREATE TYPE IF NOT EXISTS query_scope AS ENUM ('global', 'selected');

-- ============================================================================
-- Table 1: chat_session
-- Purpose: User chat sessions with conversation history
-- ============================================================================

CREATE TABLE IF NOT EXISTS chat_session (
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

-- Indexes for chat_session
CREATE INDEX IF NOT EXISTS idx_chat_session_user ON chat_session(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_chat_session_active ON chat_session(is_active, last_active DESC);
CREATE INDEX IF NOT EXISTS idx_chat_session_created ON chat_session(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_session_expire ON chat_session(last_active)
    WHERE is_active = TRUE AND last_active < CURRENT_TIMESTAMP - INTERVAL '90 days';

-- ============================================================================
-- Table 2: book_content
-- Purpose: Chunked book content with metadata (vectors stored in Qdrant)
-- ============================================================================

CREATE TABLE IF NOT EXISTS book_content (
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

-- Indexes for book_content
CREATE INDEX IF NOT EXISTS idx_book_content_module ON book_content(module_id);
CREATE INDEX IF NOT EXISTS idx_book_content_chapter ON book_content(chapter_id);
CREATE INDEX IF NOT EXISTS idx_book_content_hash ON book_content(content_hash);
CREATE INDEX IF NOT EXISTS idx_book_content_created ON book_content(created_at DESC);

-- Trigger function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for book_content
DROP TRIGGER IF EXISTS update_book_content_updated_at ON book_content;
CREATE TRIGGER update_book_content_updated_at
    BEFORE UPDATE ON book_content
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Table 3: chat_message
-- Purpose: Individual messages (user queries and assistant responses)
-- ============================================================================

CREATE TABLE IF NOT EXISTS chat_message (
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

-- Indexes for chat_message
CREATE INDEX IF NOT EXISTS idx_chat_message_session ON chat_message(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_message_role ON chat_message(role);
CREATE INDEX IF NOT EXISTS idx_chat_message_timestamp ON chat_message(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_message_chunks ON chat_message USING GIN (retrieved_chunks);

-- Trigger function to update session on new message
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

-- Trigger for chat_message
DROP TRIGGER IF EXISTS update_session_activity ON chat_message;
CREATE TRIGGER update_session_activity
    AFTER INSERT ON chat_message
    FOR EACH ROW
    EXECUTE FUNCTION update_session_on_message();

-- ============================================================================
-- Table 4: retrieval_log
-- Purpose: Analytics and debugging for RAG retrieval quality
-- ============================================================================

CREATE TABLE IF NOT EXISTS retrieval_log (
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

-- Indexes for retrieval_log
CREATE INDEX IF NOT EXISTS idx_retrieval_log_session ON retrieval_log(session_id) WHERE session_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_retrieval_log_timestamp ON retrieval_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_retrieval_log_scope ON retrieval_log(query_scope);
CREATE INDEX IF NOT EXISTS idx_retrieval_log_results ON retrieval_log USING GIN (top_k_results);
CREATE INDEX IF NOT EXISTS idx_retrieval_log_selected ON retrieval_log USING GIN (selected_chunks);
CREATE INDEX IF NOT EXISTS idx_retrieval_log_embedding ON retrieval_log
    USING ivfflat (query_embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- Verification
-- ============================================================================

-- Verify tables exist
SELECT 'Tables created successfully:' AS status;
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
