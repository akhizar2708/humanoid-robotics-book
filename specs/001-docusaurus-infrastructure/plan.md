# Implementation Plan: Docusaurus Infrastructure + RAG Chatbot

**Branch**: `001-docusaurus-infrastructure` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-docusaurus-infrastructure/spec.md` + RAG chatbot integration requirements

**Note**: This plan covers the complete book platform including Docusaurus static site generation AND embedded RAG chatbot with FastAPI backend.

## Summary

Build a complete technical book platform using Docusaurus for static site generation with MDX content support, deployed to GitHub Pages with automated CI/CD. Integrate an embedded RAG chatbot powered by FastAPI backend, Qdrant vector database, Neon Serverless Postgres, and OpenAI Agents/ChatKit for context-aware Q&A. The system must support global and selected-text queries, provide section-level citations, and run entirely on free-tier services.

**Technical Approach**:
- **Frontend**: Docusaurus 3.x for static site with custom React component for chatbot UI
- **Content**: MDX files organized in modules (1-4) with chapters as separate documentation pages
- **Backend**: FastAPI for RAG endpoints, document ingestion, and embedding generation
- **Storage**: Qdrant Cloud (free tier) for vector embeddings, Neon Postgres for metadata/chat history
- **Deployment**: GitHub Actions for automated build/deploy to GitHub Pages
- **RAG**: OpenAI text-embedding-3-small for embeddings, GPT-3.5-turbo/GPT-4 for generation with strict grounding

## Technical Context

**Language/Version**: JavaScript/TypeScript (Node.js 18+) for frontend, Python 3.11+ for backend
**Primary Dependencies**:
  - Frontend: Docusaurus 3.x, React 18, @chatscope/chat-ui-kit-react
  - Backend: FastAPI 0.109+, LangChain 0.1+, Qdrant-client 1.7+, psycopg2 2.9+, OpenAI 1.x
**Storage**: Qdrant Cloud (vector DB, free tier 1GB), Neon Serverless Postgres (metadata, free tier 512MB)
**Testing**: Jest + React Testing Library (frontend), pytest + httpx (backend), Playwright (E2E)
**Target Platform**: Static site on GitHub Pages (frontend), Linux server/container (backend API)
**Project Type**: Web application (static frontend + API backend)
**Performance Goals**:
  - Page load <3s on 10Mbps connection (Lighthouse 90+ desktop, 80+ mobile)
  - RAG query response <2s end-to-end
  - Embedding generation <1s per 1000 tokens
  - Build time <2min for full site
**Constraints**:
  - Free-tier limits: Qdrant 1GB storage, Neon 512MB storage, GitHub Pages 100GB bandwidth/month
  - API rate limits: OpenAI tier-dependent (assume 3 RPM minimum for embeddings, 60 RPM for chat)
  - Zero hallucination: RAG must return "insufficient context" when retrieval fails
  - Selected-text queries must scope to user selection only
**Scale/Scope**:
  - Initial: 4 modules × 3-5 chapters = 12-20 pages, ~50,000 words total
  - Vector DB: ~1000 chunks (512-1024 tokens each), ~1536-dim embeddings
  - Concurrent users: 10-50 expected, 100 max supported on free tier

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-First Reproducible Development
✅ **PASS** - Specification complete with clear user stories and success criteria. All implementation steps documented in this plan with explicit dependencies and reproducible setup instructions.

### Principle II: Technical Accuracy from Authoritative Sources
✅ **PASS** - Plan references official documentation (Docusaurus docs, FastAPI docs, Qdrant docs, OpenAI API docs). Code examples will cite authoritative sources. Research phase includes verification against official docs.

### Principle III: Professional Developer Clarity
✅ **PASS** - Plan targets developers with clear technical specifications. Quickstart will provide step-by-step setup. FK grade 10-12 maintained in documentation.

### Principle IV: Modular Maintainable Content
✅ **PASS** - Content organized in discrete modules (1-4) with independent chapters. Frontend and backend separated. Docusaurus plugins isolate chatbot integration.

### Principle V: Zero Hallucination RAG Constraint
✅ **PASS** - Design includes strict grounding prompt template, "insufficient context" fallback, and retrieval confidence thresholds. Citation extraction mandatory for all responses.

### Principle VI: Selected Text Query Support
✅ **PASS** - API design includes `query_scope` parameter (global/selected). Frontend captures text selection via `window.getSelection()`. Retrieval filtered to selected content only.

### Principle VII: Free-Tier Production Viability
✅ **PASS** - Architecture uses Qdrant Cloud free tier (1GB), Neon free tier (512MB), GitHub Pages free hosting. Documentation includes free-tier setup instructions.

### Technical Stack Alignment
✅ **PASS** - Matches constitutional stack:
  - Frontend: Docusaurus ✓
  - RAG UI: React component with ChatKit ✓
  - Backend: FastAPI ✓
  - Vector DB: Qdrant Cloud ✓
  - Relational DB: Neon Postgres ✓
  - Embeddings: OpenAI text-embedding-3-small ✓
  - LLM: OpenAI GPT-3.5-turbo/GPT-4 ✓

**Gate Result**: ✅ ALL CHECKS PASS - Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-docusaurus-infrastructure/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology decisions and patterns
├── data-model.md        # Phase 1 output - entities and schemas
├── quickstart.md        # Phase 1 output - setup and development guide
├── contracts/           # Phase 1 output - API specifications
│   ├── rag-api.yaml     # OpenAPI spec for RAG endpoints
│   └── embedding-api.yaml # OpenAPI spec for document ingestion
├── checklists/
│   └── requirements.md  # Quality validation (already exists)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Docusaurus Frontend
book/                              # Docusaurus site root
├── docs/                          # Book content (MDX files)
│   ├── module-1/                  # Module 1: ROS 2
│   │   ├── chapter-1.md          # Chapter files
│   │   ├── chapter-2.md
│   │   └── chapter-3.md
│   ├── module-2/                  # Module 2 (future)
│   ├── module-3/                  # Module 3 (future)
│   └── module-4/                  # Module 4 (future)
├── src/
│   ├── components/                # Custom React components
│   │   └── ChatbotWidget/        # Embedded chatbot UI
│   │       ├── ChatbotWidget.tsx
│   │       ├── ChatbotWidget.module.css
│   │       └── index.ts
│   ├── css/                       # Custom styles
│   │   └── custom.css
│   └── pages/                     # Custom pages (homepage, etc.)
│       └── index.tsx
├── static/                        # Static assets (images, files)
│   └── img/
├── docusaurus.config.js          # Docusaurus configuration
├── sidebars.js                    # Navigation structure
├── package.json
└── tsconfig.json

# FastAPI Backend
backend/
├── src/
│   ├── api/                       # FastAPI routes
│   │   ├── __init__.py
│   │   ├── rag.py                # RAG query endpoints
│   │   └── ingest.py             # Document ingestion endpoints
│   ├── models/                    # Pydantic models and DB schemas
│   │   ├── __init__.py
│   │   ├── documents.py          # Document metadata models
│   │   ├── queries.py            # Query request/response models
│   │   └── embeddings.py         # Embedding models
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── embedder.py           # OpenAI embedding generation
│   │   ├── retriever.py          # Qdrant vector search
│   │   ├── generator.py          # OpenAI chat completion with grounding
│   │   ├── citation_extractor.py # Extract section citations from responses
│   │   └── ingestion.py          # MDX parsing and chunking
│   ├── db/                        # Database clients
│   │   ├── __init__.py
│   │   ├── qdrant_client.py      # Qdrant connection and operations
│   │   └── postgres_client.py    # Neon Postgres connection
│   ├── config.py                  # Configuration and environment variables
│   └── main.py                    # FastAPI app entry point
├── tests/
│   ├── unit/                      # Unit tests
│   │   ├── test_embedder.py
│   │   ├── test_retriever.py
│   │   └── test_generator.py
│   ├── integration/               # Integration tests
│   │   ├── test_rag_endpoints.py
│   │   └── test_ingestion.py
│   └── contract/                  # Contract tests (OpenAPI validation)
│       └── test_api_contract.py
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── Dockerfile                     # Container definition (optional for deployment)
├── .env.example                   # Environment variable template
└── README.md                      # Backend setup instructions

# CI/CD and Infrastructure
.github/
└── workflows/
    ├── deploy-book.yml            # Build and deploy Docusaurus to GitHub Pages
    ├── test-backend.yml           # Backend pytest CI
    └── test-frontend.yml          # Frontend Jest CI

# Configuration
.env.example                        # Environment variables template (API keys, DB URLs)
.gitignore                          # Ignore node_modules, venv, .env, build artifacts
README.md                           # Project overview and setup instructions
```

**Structure Decision**: Web application structure selected due to:
1. **Frontend**: Docusaurus static site generator requires Node.js ecosystem (React, webpack)
2. **Backend**: FastAPI requires Python ecosystem for RAG services
3. **Separation of Concerns**: Frontend builds to static files (deployed to GitHub Pages), backend runs as API service (deployed separately or containerized)
4. **Development Workflow**: Independent dev servers (Docusaurus dev server on port 3000, FastAPI dev server on port 8000)

Frontend (`book/`) and backend (`backend/`) are siblings at repository root, enabling independent builds and deployments.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations detected. All checks passed. This section remains empty.

## Phase 0: Outline & Research

**Status**: To be completed
**Output**: `research.md`

### Research Tasks

1. **Docusaurus Configuration Best Practices**
   - Research: Optimal Docusaurus 3.x configuration for technical book sites
   - Decisions needed: Theme selection (classic vs custom), plugin choices (search, analytics), MDX configuration
   - Sources: Docusaurus official docs, technical documentation sites using Docusaurus (React docs, Jest docs)

2. **MDX Content Organization for Multi-Module Books**
   - Research: Best practices for organizing large documentation sites with modules and chapters
   - Decisions needed: Directory structure (flat vs nested), sidebar configuration, frontmatter conventions
   - Sources: Docusaurus docs on content organization, open-source technical books on GitHub

3. **FastAPI + Qdrant Integration Patterns**
   - Research: Optimal FastAPI project structure for RAG applications, Qdrant client usage patterns
   - Decisions needed: Async vs sync Qdrant client, connection pooling, retry logic
   - Sources: FastAPI best practices, Qdrant Python client docs, LangChain integration examples

4. **Embedding Strategy for Technical Content**
   - Research: Chunking strategies for technical documentation (chunk size, overlap, semantic boundaries)
   - Decisions needed: Chunk size (512 vs 1024 tokens), overlap (0 vs 128 tokens), splitter type (character vs semantic)
   - Sources: OpenAI embedding best practices, LangChain text splitters, research papers on RAG chunk size

5. **Zero-Hallucination RAG Prompt Engineering**
   - Research: Prompt templates that enforce strict grounding and explicit "I don't know" responses
   - Decisions needed: System prompt structure, few-shot examples, citation formatting
   - Sources: OpenAI prompt engineering guide, RAG best practices, academic papers on faithful generation

6. **Selected-Text Query Implementation**
   - Research: Browser APIs for text selection, scoped retrieval strategies, UX patterns
   - Decisions needed: Selection capture method (`window.getSelection()` vs custom), backend filtering approach
   - Sources: MDN Web APIs, RAG UX patterns, accessibility guidelines for text selection

7. **Free-Tier Optimization Strategies**
   - Research: Techniques to stay within Qdrant 1GB, Neon 512MB, OpenAI rate limits
   - Decisions needed: Caching strategy (Redis vs in-memory), request batching, embedding reuse
   - Sources: Qdrant optimization docs, Neon performance tuning, cost optimization guides

8. **GitHub Actions Deployment Pipeline**
   - Research: Best practices for deploying Docusaurus to GitHub Pages, secrets management
   - Decisions needed: Build trigger (push vs PR), caching strategy, deployment branch
   - Sources: Docusaurus deployment docs, GitHub Actions marketplace, CI/CD best practices

### Expected Outcomes

`research.md` will contain:
- **Technology Decisions**: Docusaurus version/theme, FastAPI project structure, Qdrant client config
- **Architecture Patterns**: Embedding pipeline, RAG query flow, selected-text handling
- **Configuration Choices**: Chunk size (1024 tokens), overlap (128 tokens), embedding model (text-embedding-3-small)
- **Prompt Templates**: Zero-hallucination system prompt, citation format, fallback messages
- **Deployment Strategy**: GitHub Actions workflow structure, environment variable management
- **Alternatives Considered**: Why chosen over alternatives (e.g., VitePress vs Docusaurus, Pinecone vs Qdrant)

All decisions will include rationale and references to authoritative sources.

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete
**Status**: To be completed
**Outputs**: `data-model.md`, `contracts/`, `quickstart.md`, updated agent context

### Data Model (`data-model.md`)

Entities derived from feature spec and technical requirements:

1. **BookContent** (MDX files → Qdrant + Postgres)
   - `id` (UUID): Unique identifier for content chunk
   - `module_id` (string): Module identifier (e.g., "module-1")
   - `chapter_id` (string): Chapter identifier (e.g., "chapter-1")
   - `section_title` (string): Section heading
   - `content_text` (string): Raw text content (512-1024 tokens)
   - `content_embedding` (vector[1536]): OpenAI text-embedding-3-small output
   - `metadata` (JSON): Additional context (page URL, heading level, code language)
   - **Validation**: content_text 100-2000 characters, embedding dimension = 1536
   - **Relationships**: Belongs to Module and Chapter

2. **ChatSession** (Postgres only)
   - `session_id` (UUID): Unique session identifier
   - `user_id` (string, optional): User identifier (future enhancement)
   - `created_at` (timestamp): Session creation time
   - `last_active` (timestamp): Last interaction time
   - **Validation**: created_at <= last_active
   - **Relationships**: Has many ChatMessages

3. **ChatMessage** (Postgres only)
   - `message_id` (UUID): Unique message identifier
   - `session_id` (UUID, FK): References ChatSession
   - `role` (enum: user, assistant): Message sender
   - `content` (text): Message text
   - `query_scope` (enum: global, selected): Query type (user messages only)
   - `selected_text` (text, nullable): Text selection for scoped queries
   - `retrieved_chunks` (JSON): IDs of chunks used for response (assistant messages only)
   - `timestamp` (timestamp): Message creation time
   - **Validation**: role ∈ {user, assistant}, query_scope required if role=user
   - **Relationships**: Belongs to ChatSession

4. **RetrievalLog** (Postgres only - for debugging/analytics)
   - `log_id` (UUID): Unique log identifier
   - `query_text` (text): User query
   - `query_embedding` (vector[1536]): Query embedding
   - `top_k_results` (JSON): Retrieved chunk IDs and scores
   - `selected_chunks` (JSON): Chunks actually used in generation
   - `timestamp` (timestamp): Query time
   - **Validation**: top_k_results is valid JSON array
   - **Relationships**: Standalone (for analytics)

### API Contracts (`contracts/`)

#### RAG Query API (`rag-api.yaml` - OpenAPI 3.0)

**Endpoint**: `POST /api/v1/query`

**Request**:
```yaml
QueryRequest:
  type: object
  required: [query, query_scope, session_id]
  properties:
    query:
      type: string
      minLength: 1
      maxLength: 1000
      description: User's question
    query_scope:
      type: string
      enum: [global, selected]
      description: Query scope (entire book or selected text)
    selected_text:
      type: string
      nullable: true
      description: Selected text content (required if query_scope=selected)
    session_id:
      type: string
      format: uuid
      description: Chat session identifier
    top_k:
      type: integer
      default: 5
      minimum: 1
      maximum: 20
      description: Number of chunks to retrieve
```

**Response** (200 OK):
```yaml
QueryResponse:
  type: object
  required: [answer, citations, retrieved_chunks]
  properties:
    answer:
      type: string
      description: Generated answer (or "I don't have enough information...")
    citations:
      type: array
      items:
        type: object
        properties:
          section_title: string
          module_id: string
          chapter_id: string
          page_url: string
      description: Sections cited in the answer
    retrieved_chunks:
      type: array
      items:
        type: object
        properties:
          chunk_id: string
          score: number (0-1)
          content_preview: string (first 200 chars)
      description: Retrieved chunks with relevance scores
    confidence:
      type: number
      minimum: 0
      maximum: 1
      description: Answer confidence score
```

**Error Responses**:
- 400: Invalid request (missing required fields, invalid query_scope)
- 429: Rate limit exceeded (OpenAI API limits)
- 500: Server error (database connection, API failures)

#### Document Ingestion API (`embedding-api.yaml`)

**Endpoint**: `POST /api/v1/ingest`

**Request**:
```yaml
IngestRequest:
  type: object
  required: [content_files]
  properties:
    content_files:
      type: array
      items:
        type: object
        properties:
          file_path: string (e.g., "docs/module-1/chapter-1.md")
          content: string (MDX content)
          metadata:
            type: object
            properties:
              module_id: string
              chapter_id: string
              section_title: string
```

**Response** (200 OK):
```yaml
IngestResponse:
  type: object
  properties:
    chunks_created: integer
    embeddings_generated: integer
    status: string (enum: success, partial, failed)
    errors: array of string (optional)
```

**Internal Logic**:
1. Parse MDX → extract sections
2. Chunk text (1024 tokens, 128 overlap)
3. Generate embeddings via OpenAI API
4. Store in Qdrant (vectors) + Postgres (metadata)

### Quickstart Guide (`quickstart.md`)

Covers:
1. **Prerequisites**: Node.js 18+, Python 3.11+, Git
2. **Environment Setup**: Clone repo, install dependencies, configure .env
3. **Database Setup**: Qdrant Cloud account, Neon Postgres account, API keys
4. **Local Development**: Run Docusaurus dev server, run FastAPI dev server
5. **Content Ingestion**: Run ingestion script to populate vector DB
6. **Testing**: Run frontend tests, backend tests, E2E tests
7. **Deployment**: GitHub Actions workflow, environment variables in GitHub Secrets
8. **Troubleshooting**: Common issues (CORS, API rate limits, environment variables)

### Agent Context Update

Run: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Additions**:
- Docusaurus 3.x project structure
- FastAPI + Qdrant + Neon Postgres integration patterns
- RAG query endpoint contracts
- Zero-hallucination prompt templates
- Selected-text query implementation

## Phase 2: Task Generation

**Prerequisites**: Phase 1 complete
**Output**: `tasks.md` (created by `/sp.tasks` command, NOT by `/sp.plan`)

Tasks will be organized by user story:
- **P1 Tasks**: Docusaurus setup, MDX content structure, local dev server
- **P2 Tasks**: GitHub Actions workflow, GitHub Pages deployment
- **P3 Tasks**: Theme customization, navigation structure, branding
- **P4 Tasks**: FastAPI backend, Qdrant integration, RAG endpoints, chatbot UI component

This phase is executed by a separate command (`/sp.tasks`) after planning is complete.

## Next Steps

1. Complete Phase 0: Generate `research.md` by researching all identified decision points
2. Complete Phase 1: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. Run `/sp.tasks` to generate implementation task list
4. Begin implementation following task priorities (P1 → P2 → P3 → P4)

**Current Status**: Planning complete. Ready for Phase 0 research execution.
