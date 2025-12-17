# Quickstart Guide: Docusaurus Infrastructure + RAG Chatbot

**Feature**: 001-docusaurus-infrastructure
**Created**: 2025-12-16
**Status**: Ready for Implementation
**Prerequisites**: research.md, data-model.md, contracts/

This guide walks you through setting up the complete technical book platform with embedded RAG chatbot from scratch.

---

## Overview

**What You'll Build:**
- Docusaurus 3.x static site with 4 educational modules
- FastAPI backend with RAG query and document ingestion endpoints
- Vector database (Qdrant Cloud) for semantic search
- Metadata database (Neon Serverless Postgres)
- CI/CD deployment to GitHub Pages

**Architecture:**
```
┌─────────────────────┐      ┌──────────────────────┐
│   Docusaurus Site   │─────▶│   FastAPI Backend    │
│  (GitHub Pages)     │      │   (localhost:8000)   │
│                     │      │                      │
│  - docs/ (MDX)      │      │  - /api/v1/query     │
│  - ChatbotWidget    │      │  - /api/v1/ingest    │
└─────────────────────┘      └──────────────────────┘
                                      │
                        ┌─────────────┴─────────────┐
                        ▼                           ▼
                 ┌──────────────┐          ┌──────────────┐
                 │    Qdrant    │          │     Neon     │
                 │   (vectors)  │          │  (metadata)  │
                 └──────────────┘          └──────────────┘
```

**Estimated Setup Time**: 30-45 minutes

---

## 1. Prerequisites

### Required Software

**Node.js 18+** (for Docusaurus):
```bash
# Verify installation
node --version  # Should be >= 18.0.0
npm --version   # Should be >= 9.0.0

# Download from: https://nodejs.org/
```

**Python 3.11+** (for FastAPI backend):
```bash
# Verify installation
python --version  # Should be >= 3.11.0
pip --version     # Should be >= 23.0.0

# Download from: https://www.python.org/downloads/
```

**Git** (version control):
```bash
# Verify installation
git --version  # Should be >= 2.30.0

# Download from: https://git-scm.com/downloads
```

### Cloud Services (Free Tier)

**Qdrant Cloud** (vector database):
- Sign up: https://cloud.qdrant.io/
- Create cluster (free tier: 1GB storage)
- Note your cluster URL and API key

**Neon Serverless Postgres** (metadata database):
- Sign up: https://neon.tech/
- Create project (free tier: 512MB storage)
- Note your connection string

**OpenAI API** (embeddings + generation):
- Sign up: https://platform.openai.com/
- Create API key
- Note your organization ID

---

## 2. Environment Setup

### 2.1 Clone Repository

```bash
# Clone the repo
git clone https://github.com/your-username/ai-humanoid-robotics-book.git
cd ai-humanoid-robotics-book

# Verify structure
ls -la
# Should see: book/, backend/, specs/, .github/
```

### 2.2 Configure Environment Variables

Create `.env` files for both frontend and backend.

**Backend `.env`** (location: `backend/.env`):

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
OPENAI_ORG_ID=org-xxxxxxxxxxxxxxxxxxxx

# Qdrant Configuration
QDRANT_URL=https://xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.us-east-1.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=xxxxxxxxxxxxxxxxxxxx
QDRANT_COLLECTION_NAME=book_content

# Neon Postgres Configuration
DATABASE_URL=postgresql://username:password@ep-xxxx-xxxx.us-east-1.aws.neon.tech/dbname?sslmode=require

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://your-username.github.io

# Rate Limiting
QUERY_RATE_LIMIT=10  # queries per minute per session
INGEST_RATE_LIMIT=5  # ingestions per hour

# Logging
LOG_LEVEL=INFO
```

**Frontend `.env`** (location: `book/.env`):

```bash
# API Endpoint
REACT_APP_API_URL=http://localhost:8000

# For production (GitHub Pages)
# REACT_APP_API_URL=https://api.your-domain.com
```

**IMPORTANT**: Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
echo "backend/.env" >> .gitignore
echo "book/.env" >> .gitignore
```

### 2.3 Install Dependencies

**Backend Dependencies:**

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# requirements.txt contents:
# fastapi==0.109.0
# uvicorn[standard]==0.27.0
# qdrant-client==1.7.0
# asyncpg==0.29.0
# langchain==0.1.0
# langchain-openai==0.0.2
# openai==1.10.0
# tiktoken==0.5.2
# python-dotenv==1.0.0
# pydantic==2.5.3
# pydantic-settings==2.1.0
```

**Frontend Dependencies:**

```bash
cd ../book
npm install

# Key dependencies installed:
# @docusaurus/core: 3.x
# @docusaurus/preset-classic: 3.x
# @chatscope/chat-ui-kit-react: ^1.10.1
# react: 18.x
# react-dom: 18.x
```

---

## 3. Database Setup

### 3.1 Initialize Qdrant Collection

```bash
cd backend
python scripts/init_qdrant.py
```

**Expected Output:**
```
✓ Connected to Qdrant Cloud
✓ Created collection 'book_content'
✓ Enabled int8 quantization
✓ Collection ready for ingestion
```

**What This Does:**
- Creates `book_content` collection with 1536-dimensional vectors
- Configures cosine similarity for semantic search
- Enables int8 quantization for 75% storage reduction

### 3.2 Initialize Postgres Schema

```bash
cd backend
psql $DATABASE_URL -f scripts/init_postgres.sql
```

**Expected Output:**
```
CREATE EXTENSION
CREATE TYPE
CREATE TYPE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX (x12)
CREATE FUNCTION
CREATE TRIGGER (x2)
```

**What This Does:**
- Creates 4 tables: `book_content`, `chat_session`, `chat_message`, `retrieval_log`
- Installs pgvector extension for vector operations
- Creates indexes for fast lookups
- Sets up triggers for automatic timestamp updates

**Verify Setup:**

```bash
# Check tables exist
psql $DATABASE_URL -c "\dt"
```

Expected tables:
```
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+---------
 public | book_content    | table | user
 public | chat_session    | table | user
 public | chat_message    | table | user
 public | retrieval_log   | table | user
```

---

## 4. Local Development

### 4.1 Start Backend Server

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Health Check:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

**API Documentation:**
Open in browser: http://localhost:8000/docs

### 4.2 Start Frontend Server

In a **new terminal**:

```bash
cd book
npm start
```

**Expected Output:**
```
[SUCCESS] Docusaurus website is running at: http://localhost:3000/
```

**Verify:**
Open browser to http://localhost:3000/
- Homepage should load
- Navigation should work
- Chatbot widget should appear in bottom-right corner

---

## 5. Content Ingestion

Before the chatbot can answer questions, you must ingest the book content into the vector database.

### 5.1 Prepare Content Files

Ensure your MDX files are in the correct structure:

```
book/docs/
├── module-1/
│   ├── _category_.json
│   ├── chapter-1.md
│   ├── chapter-2.md
│   └── chapter-3.md
├── module-2/
│   ├── _category_.json
│   └── ...
├── module-3/
│   └── ...
└── module-4/
    └── ...
```

**Example `_category_.json`:**
```json
{
  "label": "Module 1: The Robotic Nervous System",
  "position": 1,
  "collapsible": true,
  "collapsed": false
}
```

**Example Chapter Frontmatter** (`chapter-1.md`):
```yaml
---
title: "ROS 2 Fundamentals for Physical AI"
sidebar_position: 1
---

# ROS 2 Fundamentals for Physical AI

ROS 2 is a middleware framework...
```

### 5.2 Run Ingestion Script

```bash
cd backend
python scripts/ingest_content.py --docs-dir ../book/docs
```

**Expected Output:**
```
[INFO] Scanning docs directory: ../book/docs
[INFO] Found 12 chapters across 4 modules
[INFO] Processing module-1/chapter-1.md...
  ✓ Parsed 1,245 words
  ✓ Created 3 chunks (avg: 415 words/chunk)
  ✓ Generated 3 embeddings
  ✓ Stored in Qdrant + Postgres
[INFO] Processing module-1/chapter-2.md...
  ...
[SUCCESS] Ingestion complete
  - Chunks created: 45
  - Embeddings generated: 45
  - Processing time: 42.3s
```

**Verify Ingestion:**

```bash
# Check Postgres
psql $DATABASE_URL -c "SELECT COUNT(*) FROM book_content;"
# Expected: 45 (or your actual chunk count)

# Check ingestion status via API
curl http://localhost:8000/api/v1/ingest/status
```

Expected response:
```json
{
  "total_chunks": 45,
  "total_embeddings": 45,
  "modules": [
    {
      "module_id": "module-1",
      "chunk_count": 12,
      "last_updated": "2025-12-16T10:30:00Z"
    }
  ],
  "storage_usage": {
    "qdrant_mb": 0.8,
    "postgres_mb": 1.2
  }
}
```

### 5.3 Test RAG Query

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

Expected response (example):
```json
{
  "answer": "ROS 2 is a middleware framework for robotics applications that provides publish-subscribe messaging, service calls, and action servers for building distributed robotic systems [Module 1, Chapter 1].",
  "citations": [
    {
      "section_title": "ROS 2 Fundamentals for Physical AI",
      "module_id": "module-1",
      "chapter_id": "chapter-1",
      "page_url": "/module-1/chapter-1"
    }
  ],
  "retrieved_chunks": [
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440001",
      "score": 0.89,
      "content_preview": "ROS 2 is a middleware framework that provides..."
    }
  ],
  "confidence": 0.95
}
```

---

## 6. Testing

### 6.1 Backend Tests

```bash
cd backend
pytest tests/ -v
```

**Test Coverage:**
- Unit tests: `tests/unit/`
  - `test_embedder.py` - Embedding generation
  - `test_retriever.py` - Vector search
  - `test_generator.py` - Answer generation
- Integration tests: `tests/integration/`
  - `test_api_query.py` - RAG endpoint
  - `test_api_ingest.py` - Ingestion endpoint
- E2E tests: `tests/e2e/`
  - `test_rag_workflow.py` - Full query → answer flow

**Expected Output:**
```
tests/unit/test_embedder.py::test_embed_text_success PASSED
tests/unit/test_embedder.py::test_batch_embed PASSED
tests/unit/test_retriever.py::test_retrieve_chunks PASSED
tests/integration/test_api_query.py::test_query_global PASSED
tests/integration/test_api_query.py::test_query_selected PASSED
tests/e2e/test_rag_workflow.py::test_full_rag_workflow PASSED

================ 12 passed in 8.45s ================
```

### 6.2 Frontend Tests

```bash
cd book
npm test
```

**Test Coverage:**
- Component tests: `src/__tests__/`
  - `ChatbotWidget.test.js` - Widget rendering
  - `MessageList.test.js` - Message display
  - `InputBox.test.js` - User input handling

### 6.3 Manual Testing Checklist

**Frontend:**
- [ ] Homepage loads successfully
- [ ] All 4 modules appear in sidebar
- [ ] Clicking module expands chapters
- [ ] Chapter pages render MDX correctly
- [ ] Code blocks have syntax highlighting
- [ ] Chatbot widget appears in bottom-right
- [ ] Clicking widget opens chat interface

**Chatbot - Global Query:**
- [ ] Type "What is ROS 2?" and send
- [ ] Response appears within 5 seconds
- [ ] Response includes citation (e.g., "[Module 1, Chapter 1]")
- [ ] Citation is clickable and navigates to correct page

**Chatbot - Selected Text Query:**
- [ ] Highlight text on any chapter page
- [ ] Right-click → "Ask about this"
- [ ] Chatbot opens with selected text context
- [ ] Type "What does this mean?" and send
- [ ] Response is grounded in selected text

**Edge Cases:**
- [ ] Query outside book scope returns "I don't have enough information"
- [ ] Empty query shows validation error
- [ ] Network error shows retry option

---

## 7. Deployment

### 7.1 GitHub Actions Setup

**Create Workflow File** (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: book/package-lock.json

      - name: Install dependencies
        run: |
          cd book
          npm ci

      - name: Build website
        env:
          REACT_APP_API_URL: https://api.your-domain.com
        run: |
          cd book
          npm run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: book/build

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### 7.2 Configure GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Wait for workflow to complete
4. Site will be live at: `https://your-username.github.io/ai-humanoid-robotics-book/`

### 7.3 Configure Backend Deployment

For production, deploy FastAPI backend to a cloud service (options):

**Option 1: Render.com** (free tier available):
```bash
# render.yaml
services:
  - type: web
    name: book-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: DATABASE_URL
        sync: false
```

**Option 2: Railway.app**:
```bash
# railway.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Option 3: Fly.io**:
```bash
fly launch
fly secrets set OPENAI_API_KEY=sk-proj-xxxxx
fly secrets set QDRANT_URL=https://xxxxx.cloud.qdrant.io:6333
fly secrets set DATABASE_URL=postgresql://xxxxx
fly deploy
```

### 7.4 Update Frontend API URL

After deploying backend, update frontend environment variable:

```bash
# In GitHub repository settings → Secrets → Actions
# Add secret: REACT_APP_API_URL
# Value: https://your-api-domain.com
```

Update workflow to use secret:
```yaml
- name: Build website
  env:
    REACT_APP_API_URL: ${{ secrets.REACT_APP_API_URL }}
  run: |
    cd book
    npm run build
```

---

## 8. Troubleshooting

### Issue 1: CORS Errors in Browser Console

**Symptom:**
```
Access to fetch at 'http://localhost:8000/api/v1/query' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
Check backend CORS configuration in `backend/src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

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

Ensure `CORS_ORIGINS` in `.env` includes frontend URL.

### Issue 2: OpenAI Rate Limit Exceeded

**Symptom:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "OpenAI API rate limit exceeded. Please try again in 60 seconds."
  }
}
```

**Solution:**
1. **Check your OpenAI tier**: https://platform.openai.com/account/limits
   - Tier 1: 3 RPM (very limiting)
   - Tier 2: 60 RPM (sufficient for testing)

2. **Implement caching** (already in code):
   ```python
   # In backend/src/services/embedder.py
   query_cache = TTLCache(maxsize=1000, ttl=3600)
   ```

3. **Reduce batch size** during ingestion:
   ```python
   # In backend/scripts/ingest_content.py
   batch_size = 10  # Reduce from 20 to 10
   ```

### Issue 3: Qdrant Connection Timeout

**Symptom:**
```
TimeoutError: Request to Qdrant timed out after 30 seconds
```

**Solution:**
1. Verify cluster URL in `.env`:
   ```bash
   echo $QDRANT_URL
   # Should be: https://xxxxx.us-east-1.aws.cloud.qdrant.io:6333
   ```

2. Check cluster status in Qdrant Cloud dashboard

3. Increase timeout in code:
   ```python
   # In backend/src/db/qdrant_client.py
   client = AsyncQdrantClient(
       url=settings.QDRANT_URL,
       api_key=settings.QDRANT_API_KEY,
       timeout=60,  # Increase from default 30s
   )
   ```

### Issue 4: Postgres Connection Error

**Symptom:**
```
asyncpg.exceptions.InvalidPasswordError: password authentication failed
```

**Solution:**
1. Verify connection string format:
   ```bash
   # Correct format:
   postgresql://user:password@host:5432/dbname?sslmode=require
   ```

2. Regenerate password in Neon dashboard if needed

3. Test connection:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

### Issue 5: Empty Responses from Chatbot

**Symptom:**
Chatbot returns "I don't have enough information" for all queries.

**Diagnosis:**
1. Check if content was ingested:
   ```bash
   curl http://localhost:8000/api/v1/ingest/status
   ```

2. If `total_chunks: 0`, run ingestion script:
   ```bash
   cd backend
   python scripts/ingest_content.py --docs-dir ../book/docs
   ```

3. Check chunk retrieval:
   ```bash
   # Query Qdrant directly
   curl -X POST https://xxxxx.cloud.qdrant.io:6333/collections/book_content/points/search \
     -H "Content-Type: application/json" \
     -H "api-key: xxxxx" \
     -d '{
       "vector": [0.1, 0.2, ...],  # Test vector
       "limit": 5
     }'
   ```

### Issue 6: Docusaurus Build Failures

**Symptom:**
```
Error: Duplicate routes found!
Attempting to create page for "/module-1/chapter-1"...
```

**Solution:**
1. Check for duplicate file paths in `book/docs/`

2. Verify `_category_.json` files don't conflict:
   ```bash
   find book/docs -name "_category_.json" -exec cat {} \;
   ```

3. Clear Docusaurus cache:
   ```bash
   cd book
   rm -rf .docusaurus
   npm run clear
   npm run build
   ```

---

## 9. Next Steps

After completing this setup:

1. **Content Creation** (Priority 1):
   - Write MDX files for all 4 modules
   - Add images, diagrams, code examples
   - Review with subject matter experts

2. **Chatbot Enhancement** (Priority 2):
   - Add conversation memory (use chat_message table)
   - Implement feedback mechanism (thumbs up/down)
   - Add source document previews

3. **Analytics Setup** (Priority 3):
   - Set up Grafana dashboard for retrieval_log table
   - Monitor query patterns and response quality
   - Track API usage and costs

4. **Testing & Quality** (Priority 4):
   - Run Lighthouse audits (target: 90+ performance)
   - Test on mobile devices
   - Conduct user acceptance testing

5. **Production Readiness** (Priority 5):
   - Add API key authentication for ingestion endpoint
   - Set up monitoring alerts (Sentry, LogRocket)
   - Create runbook for common operations
   - Document rollback procedures

---

## 10. Common Commands Reference

### Development

```bash
# Start backend dev server
cd backend && uvicorn src.main:app --reload

# Start frontend dev server
cd book && npm start

# Run all backend tests
cd backend && pytest tests/ -v

# Run frontend tests
cd book && npm test

# Lint backend code
cd backend && flake8 src/ tests/

# Lint frontend code
cd book && npm run lint
```

### Database Operations

```bash
# Connect to Postgres
psql $DATABASE_URL

# Check table sizes
psql $DATABASE_URL -c "
  SELECT schemaname, tablename,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
  FROM pg_tables
  WHERE schemaname = 'public';
"

# Clear all chat history (destructive!)
psql $DATABASE_URL -c "TRUNCATE chat_session CASCADE;"

# Re-ingest content (updates existing)
cd backend && python scripts/ingest_content.py --docs-dir ../book/docs --force
```

### Deployment

```bash
# Build Docusaurus for production
cd book && npm run build

# Preview production build locally
cd book && npm run serve

# Deploy backend to Render
git push render main

# Deploy backend to Railway
railway up

# Deploy backend to Fly.io
fly deploy
```

---

## 11. Support and Resources

### Documentation

- **Docusaurus**: https://docusaurus.io/docs
- **FastAPI**: https://fastapi.tiangolo.com/
- **Qdrant**: https://qdrant.tech/documentation/
- **Neon**: https://neon.tech/docs/introduction
- **OpenAI API**: https://platform.openai.com/docs

### Project Artifacts

- **Feature Spec**: `specs/001-docusaurus-infrastructure/spec.md`
- **Architecture Plan**: `specs/001-docusaurus-infrastructure/plan.md`
- **Technical Research**: `specs/001-docusaurus-infrastructure/research.md`
- **Data Model**: `specs/001-docusaurus-infrastructure/data-model.md`
- **API Contracts**: `specs/001-docusaurus-infrastructure/contracts/`

### Getting Help

1. Check `specs/001-docusaurus-infrastructure/plan.md` for architectural decisions
2. Review `research.md` for implementation details
3. Check API documentation: http://localhost:8000/docs
4. Create issue in project repository with reproduction steps

---

**Setup Status Checklist:**

- [ ] Prerequisites installed (Node.js 18+, Python 3.11+, Git)
- [ ] Cloud accounts created (Qdrant, Neon, OpenAI)
- [ ] Repository cloned
- [ ] Environment variables configured (.env files)
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Qdrant collection initialized
- [ ] Postgres schema initialized
- [ ] Backend server running (localhost:8000)
- [ ] Frontend server running (localhost:3000)
- [ ] Content ingested successfully
- [ ] RAG query test passed
- [ ] Manual testing completed
- [ ] GitHub Actions workflow configured
- [ ] Deployed to GitHub Pages

**You're ready to build!** 🚀
