---
id: 002
title: Docusaurus RAG Implementation Plan
stage: plan
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5
feature: 001-docusaurus-infrastructure
branch: 001-docusaurus-infrastructure
user: khizar
command: /sp.plan
labels: ["plan", "docusaurus", "rag", "fastapi", "qdrant", "neon-postgres", "chatbot"]
links:
  spec: specs/001-docusaurus-infrastructure/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-docusaurus-infrastructure/plan.md
  - history/prompts/001-docusaurus-infrastructure/002-docusaurus-rag-implementation-plan.plan.prompt.md
tests:
  - N/A (planning document)
---

## Prompt

```text
/sp.plan

1) Install and configure Docusaurus as the core technology; create Modules (1–4) and their chapters as documentation pages — every file must be written in `.md`.

2) Build the embedded RAG chatbot (FastAPI + Neon + Qdrant + OpenAI Agents/ChatKit), integrate it into Docusaurus, and deploy the site to GitHub Pages.
```

## Response snapshot

Created comprehensive implementation plan for **Docusaurus Infrastructure + RAG Chatbot** (branch: `001-docusaurus-infrastructure`) covering complete book platform with embedded AI assistant.

**Plan Scope**:
- Docusaurus 3.x static site for technical book (4 modules, MDX content)
- FastAPI backend for RAG services (query, document ingestion)
- Qdrant Cloud vector database (embeddings, free tier 1GB)
- Neon Serverless Postgres (chat history, metadata, free tier 512MB)
- OpenAI integration (text-embedding-3-small, GPT-3.5-turbo/GPT-4)
- React chatbot widget embedded in Docusaurus
- GitHub Actions CI/CD for GitHub Pages deployment

**Technical Context**:
- **Languages**: JavaScript/TypeScript (Node.js 18+) frontend, Python 3.11+ backend
- **Frontend Stack**: Docusaurus 3.x, React 18, @chatscope/chat-ui-kit-react
- **Backend Stack**: FastAPI 0.109+, LangChain 0.1+, Qdrant-client 1.7+, psycopg2, OpenAI 1.x
- **Performance Goals**: Page load <3s, RAG response <2s, build <2min, Lighthouse 90+/80+
- **Constraints**: Free-tier limits (Qdrant 1GB, Neon 512MB, GitHub 100GB/month), zero hallucination, selected-text query support
- **Scale**: 4 modules × 3-5 chapters = 12-20 pages, ~50K words, ~1000 vector chunks

**Constitution Check**: ✅ ALL 7 PRINCIPLES PASS
1. Spec-first development ✓
2. Technical accuracy from authoritative sources ✓
3. Professional clarity (FK 10-12) ✓
4. Modular maintainable content ✓
5. Zero hallucination RAG ✓
6. Selected-text query support ✓
7. Free-tier viability ✓

**Project Structure**:
- **Frontend**: `book/` (Docusaurus root with docs/, src/components/ChatbotWidget/, static/)
- **Backend**: `backend/` (FastAPI with src/api/, src/services/, src/models/, src/db/, tests/)
- **CI/CD**: `.github/workflows/` (deploy-book.yml, test-backend.yml, test-frontend.yml)
- **Docs**: `specs/001-docusaurus-infrastructure/` (plan.md, research.md, data-model.md, contracts/, quickstart.md)

**Phase 0 Research Tasks** (to be generated in research.md):
1. Docusaurus configuration best practices (theme, plugins, MDX)
2. MDX content organization for multi-module books
3. FastAPI + Qdrant integration patterns (async client, connection pooling)
4. Embedding strategy for technical content (chunk size: 1024 tokens, overlap: 128 tokens)
5. Zero-hallucination RAG prompt engineering (strict grounding, "I don't know" fallback)
6. Selected-text query implementation (window.getSelection(), backend filtering)
7. Free-tier optimization strategies (caching, batching, rate limits)
8. GitHub Actions deployment pipeline (caching, secrets management)

**Phase 1 Deliverables** (to be created):
- **data-model.md**: Entities (BookContent, ChatSession, ChatMessage, RetrievalLog) with schemas, validation, relationships
- **contracts/**: OpenAPI specs
  - `rag-api.yaml`: POST /api/v1/query (QueryRequest → QueryResponse with answer, citations, confidence)
  - `embedding-api.yaml`: POST /api/v1/ingest (IngestRequest → IngestResponse with chunk/embedding counts)
- **quickstart.md**: Prerequisites, environment setup, database setup, local dev, ingestion, testing, deployment, troubleshooting
- **Agent context update**: Add Docusaurus, FastAPI, Qdrant, RAG patterns to Claude context file

**Data Model Highlights**:
- **BookContent**: UUID id, module_id, chapter_id, section_title, content_text (512-1024 tokens), content_embedding (1536-dim vector), metadata JSON
- **ChatSession**: UUID session_id, optional user_id, timestamps
- **ChatMessage**: UUID message_id, session_id FK, role enum (user/assistant), content, query_scope enum (global/selected), selected_text, retrieved_chunks JSON
- **RetrievalLog**: Query text, query embedding, top-k results, selected chunks, timestamp (for analytics)

**API Contract Highlights**:
- **RAG Query**: POST /api/v1/query with query, query_scope (global/selected), selected_text, session_id, top_k → Returns answer, citations array (section_title, module_id, chapter_id, page_url), retrieved_chunks, confidence score
- **Ingestion**: POST /api/v1/ingest with content_files array (file_path, content, metadata) → Returns chunks_created, embeddings_generated, status
- **Error Handling**: 400 (invalid request), 429 (rate limit), 500 (server error)

**Phase 2 Task Organization** (to be generated by /sp.tasks):
- P1: Docusaurus setup, MDX content structure, local dev server
- P2: GitHub Actions workflow, GitHub Pages deployment
- P3: Theme customization, navigation, branding
- P4: FastAPI backend, Qdrant integration, RAG endpoints, chatbot widget

**Next Steps**:
1. Execute Phase 0: Generate research.md with technology decisions
2. Execute Phase 1: Generate data-model.md, contracts/, quickstart.md
3. Run /sp.tasks to create implementation task list
4. Begin implementation (P1 → P2 → P3 → P4)

Planning complete. Ready for research phase execution.

## Outcome

- ✅ Impact: Comprehensive implementation plan created for complete book platform (Docusaurus + RAG chatbot) - defines architecture, tech stack, data model, API contracts, project structure
- 🧪 Tests: Constitution check validated (7/7 principles passed)
- 📁 Files: plan.md (471 lines with detailed technical specifications, API contracts, data models, research tasks)
- 🔁 Next prompts: Begin Phase 0 research to resolve technical decisions, then Phase 1 design for contracts and quickstart
- 🧠 Reflection: Successfully integrated both Docusaurus infrastructure AND RAG chatbot requirements into unified plan. Maintained constitutional principles (free-tier, zero hallucination, selected-text queries). Plan balances frontend (static site) and backend (API services) with clear separation of concerns. Ready for execution.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan created successfully covering both infrastructure and RAG integration
- Graders run and results (PASS/FAIL): Constitution check - PASS (7/7 principles validated)
- Prompt variant (if applicable): Combined infrastructure + RAG planning - expanded scope from original spec but aligned with user's explicit requirements
- Next experiment (smallest change to try): In Phase 0 research, validate chunk size decision (1024 tokens) against technical documentation best practices; may need A/B testing to optimize retrieval quality
