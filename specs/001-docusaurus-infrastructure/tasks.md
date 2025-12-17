# Tasks: Docusaurus Infrastructure + RAG Chatbot

**Input**: Design documents from `/specs/001-docusaurus-infrastructure/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are omitted in favor of manual testing using quickstart.md validation procedures.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, RAG)
- Include exact file paths in descriptions

## Path Conventions

This is a **web application** with:
- **Frontend**: `book/` (Docusaurus static site)
- **Backend**: `backend/` (FastAPI API server)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize both Docusaurus frontend and FastAPI backend projects

- [X] T001 Create project root directory structure with npx create-docusaurus@latest frontend_book classic
- [X] T002 Initialize Docusaurus project in book/ using `npx create-docusaurus@latest book classic`
- [X] T003 [P] Initialize Python virtual environment in backend/ and create backend/requirements.txt with FastAPI 0.109+, uvicorn, qdrant-client 1.7+, asyncpg 0.29+, langchain 0.1+, openai 1.10+, tiktoken, python-dotenv, pydantic-settings
- [X] T004 [P] Create backend/requirements-dev.txt with pytest, httpx, pytest-asyncio, black, flake8
- [X] T005 [P] Create .gitignore with node_modules/, venv/, .env, build/, __pycache__/, .pytest_cache/
- [X] T006 [P] Create root-level README.md with project overview and setup instructions per quickstart.md
- [X] T007 [P] Create .env.example files in backend/ and book/ with required environment variables (OPENAI_API_KEY, QDRANT_URL, DATABASE_URL, API_HOST, API_PORT, CORS_ORIGINS, REACT_APP_API_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Infrastructure

- [X] T008 Create backend/scripts/ directory for database initialization scripts
- [X] T009 Create backend/scripts/init_qdrant.py to initialize Qdrant collection with 1536-dim vectors, cosine distance, int8 quantization per data-model.md
- [X] T010 Create backend/scripts/init_postgres.sql with complete schema from data-model.md (book_content, chat_session, chat_message, retrieval_log tables with indexes and triggers)
- [X] T011 [P] Create backend/src/db/__init__.py as empty module file
- [X] T012 [P] Create backend/src/db/qdrant_client.py with AsyncQdrantClient initialization using environment variables
- [X] T013 [P] Create backend/src/db/postgres_client.py with asyncpg connection pool setup

### Backend Configuration

- [X] T014 Create backend/src/config.py with pydantic-settings BaseSettings class for all environment variables (OpenAI, Qdrant, Postgres, API, CORS)
- [X] T015 Create backend/src/__init__.py as empty module file
- [X] T016 Create backend/src/main.py with FastAPI app initialization, CORS middleware per research.md, health check endpoint at /health
- [X] T017 Add startup event handler in backend/src/main.py to verify database connections on startup

### Backend Models

- [X] T018 [P] Create backend/src/models/__init__.py as empty module file
- [X] T019 [P] Create backend/src/models/documents.py with Pydantic models for BookContent (ContentFile, ContentMetadata from contracts/embedding-api.yaml)
- [X] T020 [P] Create backend/src/models/queries.py with Pydantic models for QueryRequest, QueryResponse, Citation, RetrievedChunk from contracts/rag-api.yaml
- [X] T021 [P] Create backend/src/models/embeddings.py with Pydantic models for IngestRequest, IngestResponse, IngestError, IngestionStatus from contracts/embedding-api.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Author Content Creation and Preview (Priority: P1) 🎯 MVP

**Goal**: Enable authors to write book content in MDX format and preview it locally with hot reload

**Independent Test**: Create a sample chapter file in book/docs/, run `npm start`, verify content appears in browser at http://localhost:3000/ with hot reload on file changes

### Implementation for User Story 1

- [X] T022 [US1] Configure book/docusaurus.config.js with site metadata (title: "AI-Driven Humanoid Robotics", tagline, URL), docs-only mode (routeBasePath: '/'), disable blog per research.md
- [X] T023 [US1] Create book/docs/ directory structure with module-1/, module-2/, module-3/, module-4/ subdirectories
- [X] T024 [P] [US1] Create book/docs/module-1/_category_.json with label "Module 1: The Robotic Nervous System", position: 1
- [X] T025 [P] [US1] Create book/docs/module-2/_category_.json with label "Module 2: Perception and Computer Vision", position: 2
- [X] T026 [P] [US1] Create book/docs/module-3/_category_.json with label "Module 3: Motion Planning and Control", position: 3
- [X] T027 [P] [US1] Create book/docs/module-4/_category_.json with label "Module 4: Integration and Deployment", position: 4
- [X] T028 [P] [US1] Create sample chapter file book/docs/module-1/chapter-1.md with frontmatter (title, sidebar_position), H1 heading, sample content including code blocks
- [X] T029 [P] [US1] Create sample chapter file book/docs/module-1/chapter-2.md with frontmatter and content
- [X] T030 [P] [US1] Create sample chapter file book/docs/module-1/chapter-3.md with frontmatter and content
- [X] T031 [US1] Configure book/sidebars.js to auto-generate sidebars from directory structure using autogenerated sidebars
- [X] T032 [US1] Configure Prism syntax highlighting in book/docusaurus.config.js for Python, JavaScript, TypeScript, Bash, JSON, YAML, SQL per research.md
- [X] T033 [US1] Test hot reload by starting dev server with `npm start` and modifying content files

**Checkpoint**: At this point, User Story 1 should be fully functional - authors can create content and preview locally

---

## Phase 4: RAG Chatbot Backend Implementation

**Goal**: Build FastAPI backend with document ingestion and RAG query capabilities

**Independent Test**: Run backend server with `uvicorn src.main:app --reload`, test /api/v1/ingest endpoint with sample content, test /api/v1/query endpoint with sample query

### Services Implementation

- [X] T034 [P] [RAG] Create backend/src/services/__init__.py as empty module file
- [X] T035 [P] [RAG] Create backend/src/services/embedder.py with async embed_text() and embed_chunks_batch() functions using OpenAI text-embedding-3-small, including TTL cache per research.md
- [X] T036 [P] [RAG] Create backend/src/services/retriever.py with async retrieve_chunks() function for Qdrant similarity search, supporting global and selected-text filtering
- [X] T037 [P] [RAG] Create backend/src/services/generator.py with async generate_answer() function using OpenAI GPT-3.5-turbo with zero-hallucination system prompt from research.md
- [X] T038 [P] [RAG] Create backend/src/services/citation_extractor.py with extract_citations() function to parse [Module X, Chapter Y] format from generated responses
- [X] T039 [RAG] Create backend/src/services/ingestion.py with parse_mdx(), chunk_text() using RecursiveCharacterTextSplitter (1024 tokens, 128 overlap), and store_chunks() functions

### API Endpoints Implementation

- [X] T040 [P] [RAG] Create backend/src/api/__init__.py as empty module file
- [X] T041 [RAG] Create backend/src/api/ingest.py with POST /api/v1/ingest endpoint implementing full ingestion flow per contracts/embedding-api.yaml (parse, chunk, embed, store in Qdrant + Postgres)
- [X] T042 [RAG] Add GET /api/v1/ingest/status endpoint in backend/src/api/ingest.py returning IngestionStatus per contracts/embedding-api.yaml
- [X] T043 [RAG] Create backend/src/api/rag.py with POST /api/v1/query endpoint implementing full RAG flow per contracts/rag-api.yaml (embed query, retrieve chunks, generate answer with citations, log to retrieval_log)
- [X] T044 [RAG] Register ingest and rag routers in backend/src/main.py with /api/v1 prefix
- [X] T045 [RAG] Add rate limiting middleware in backend/src/main.py (10 queries/minute per session, 5 ingestions/hour) per quickstart.md

### Content Ingestion Script

- [X] T046 [RAG] Create backend/scripts/ingest_content.py CLI script that scans book/docs/ directory, reads all .md files, extracts metadata from frontmatter, calls /api/v1/ingest endpoint per quickstart.md

**Checkpoint**: Backend API is fully functional - can ingest content and respond to RAG queries

---

## Phase 5: Chatbot Frontend Integration

**Goal**: Integrate chatbot UI component into Docusaurus site with global and selected-text query support

**Independent Test**: Open Docusaurus site, click chatbot widget in bottom-right, send a query, verify response with citations appears

### React Component Implementation

- [X] T047 [P] [RAG] Install @chatscope/chat-ui-kit-react and @chatscope/chat-ui-kit-styles in book/ with npm
- [X] T048 [P] [RAG] Create book/src/components/ChatbotWidget/ directory
- [X] T049 [RAG] Create book/src/components/ChatbotWidget/ChatbotWidget.tsx with main component structure (minimized/expanded states, message list, input box)
- [X] T050 [RAG] Implement sendQuery() function in ChatbotWidget.tsx to POST to /api/v1/query endpoint with query_scope: "global", handle response
- [X] T051 [RAG] Implement text selection handler in ChatbotWidget.tsx using window.getSelection() API, capture selected text, send with query_scope: "selected" per research.md
- [X] T052 [RAG] Add citation links in ChatbotWidget.tsx message renderer to navigate to book pages when clicked
- [X] T053 [RAG] Add loading indicator and error handling UI states in ChatbotWidget.tsx
- [X] T054 [RAG] Create book/src/components/ChatbotWidget/ChatbotWidget.module.css with styling for floating widget, chat interface, messages
- [X] T055 [RAG] Create book/src/components/ChatbotWidget/index.ts to export ChatbotWidget component

### Integration with Docusaurus

- [X] T056 [RAG] Create book/src/theme/Root.tsx to wrap all pages with ChatbotWidget component per Docusaurus theme customization
- [X] T057 [RAG] Configure environment variable REACT_APP_API_URL in book/.env pointing to http://localhost:8000
- [X] T058 [RAG] Test chatbot on local dev server with sample queries (global and selected-text modes)

**Checkpoint**: Chatbot is fully integrated - users can ask questions and receive answers with citations

---

## Phase 6: User Story 2 - Public Book Access via GitHub Pages (Priority: P2)

**Goal**: Deploy book to GitHub Pages for public access

**Independent Test**: Trigger deployment, wait for completion, access GitHub Pages URL (https://username.github.io/repo-name/), verify site loads and all pages are accessible

### Implementation for User Story 2

- [ ] T059 [US2] Configure book/docusaurus.config.js with correct baseUrl and url for GitHub Pages deployment (baseUrl: '/repo-name/', url: 'https://username.github.io')
- [ ] T060 [US2] Add deployment script in book/package.json for `npm run deploy` using Docusaurus deploy command
- [ ] T061 [US2] Update book/.env with production API URL (REACT_APP_API_URL pointing to deployed backend)
- [ ] T062 [US2] Run manual deployment test with `npm run build` and `npm run serve` to verify production build works locally
- [ ] T063 [US2] Configure GitHub repository settings to enable GitHub Pages with source set to gh-pages branch
- [ ] T064 [US2] Test deployed site accessibility, navigation, media assets, and chatbot functionality

**Checkpoint**: Book is publicly accessible via GitHub Pages URL

---

## Phase 7: User Story 4 - Automated Build and Deployment Pipeline (Priority: P4)

**Goal**: Automate deployment using GitHub Actions on every commit to main branch

**Independent Test**: Make a content change, commit to main branch, verify GitHub Actions workflow triggers automatically, check workflow logs for success, verify deployed site reflects changes

### Implementation for User Story 4

- [ ] T065 [US4] Create .github/workflows/ directory
- [ ] T066 [US4] Create .github/workflows/deploy-book.yml with GitHub Actions workflow per quickstart.md (triggers on push to main, sets up Node.js 18, installs dependencies, builds Docusaurus site, deploys to GitHub Pages using actions/deploy-pages@v4)
- [ ] T067 [P] [US4] Create .github/workflows/test-backend.yml with backend testing workflow (triggers on push/PR, sets up Python 3.11, installs dependencies, runs pytest)
- [ ] T068 [P] [US4] Create .github/workflows/test-frontend.yml with frontend testing workflow (triggers on push/PR, sets up Node.js, installs dependencies, runs npm test)
- [ ] T069 [US4] Configure GitHub repository secrets for production environment (REACT_APP_API_URL for frontend build)
- [ ] T070 [US4] Configure GitHub Actions permissions in repository settings (contents: read, pages: write, id-token: write)
- [ ] T071 [US4] Test automated workflow by making a sample content change and pushing to main
- [ ] T072 [US4] Verify workflow logs show successful build and deployment
- [ ] T073 [US4] Verify deployed site reflects the content change within 5 minutes

**Checkpoint**: Automated deployment works end-to-end - commits automatically trigger builds and deployments

---

## Phase 8: User Story 3 - Theme Customization and Branding (Priority: P3)

**Goal**: Customize site appearance with professional branding, colors, logo, and footer

**Independent Test**: Modify theme configuration, rebuild site, verify customizations appear correctly in both local preview and deployed site

### Implementation for User Story 3

- [X] T074 [P] [US3] Create book/static/img/ directory and add custom logo file (logo.png or logo.svg)
- [X] T075 [US3] Configure navbar logo in book/docusaurus.config.js themeConfig.navbar with src, alt, and logo link
- [X] T076 [US3] Customize color palette in book/src/css/custom.css with primary and secondary colors for light and dark modes
- [X] T077 [US3] Configure footer in book/docusaurus.config.js themeConfig.footer with copyright, useful links, social media links
- [X] T078 [US3] Customize navbar items in book/docusaurus.config.js themeConfig.navbar.items (Home, Modules, GitHub repo link)
- [X] T079 [US3] Add custom fonts in book/src/css/custom.css using @import or @font-face
- [X] T080 [US3] Configure metadata tags in book/docusaurus.config.js (description, keywords, author, Open Graph tags for social sharing)
- [X] T081 [US3] Test theme in light mode and dark mode to ensure proper contrast and readability
- [X] T082 [US3] Test responsive design on mobile devices (320px to 768px widths)

**Checkpoint**: Site has professional branding and visual polish consistent across all pages

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements that affect multiple user stories, testing, and documentation

### Documentation

- [X] T083 [P] Update root README.md with comprehensive project overview, architecture diagram, setup instructions linking to quickstart.md
- [X] T084 [P] Create backend/README.md with backend-specific setup, API documentation links, environment variables
- [X] T085 [P] Create book/README.md with frontend-specific setup, content authoring guidelines, MDX examples

### Content Guidelines

- [X] T086 [P] Create book/docs/README.md with content authoring guidelines (frontmatter format, heading structure, code block conventions, image size limits)
- [X] T087 [P] Add example templates in book/docs/templates/ for chapter-template.md showing proper structure

### Testing & Validation

- [ ] T088 Run full quickstart.md validation procedure from fresh environment (Prerequisites → Environment Setup → Database Setup → Local Development → Content Ingestion → Testing)
- [ ] T089 Verify all acceptance scenarios from spec.md (hot reload <2s, homepage load <3s, automated deployment <5min, etc.)
- [ ] T090 Run Lighthouse audits on deployed site and verify scores (90+ desktop performance, 80+ mobile performance)
- [ ] T091 [P] Test cross-browser compatibility (Chrome, Firefox, Safari) for both book site and chatbot
- [ ] T092 [P] Test chatbot edge cases (empty query, query outside book scope, network errors, rate limiting)
- [ ] T093 [P] Validate OpenAPI contracts using openapi-spec-validator on contracts/rag-api.yaml and contracts/embedding-api.yaml

### Performance & Optimization

- [ ] T094 [P] Optimize images in book/static/img/ (compress, convert to WebP where appropriate, lazy loading)
- [ ] T095 [P] Review backend/src/services/embedder.py cache configuration and adjust TTL/size based on usage patterns
- [ ] T096 [P] Add response compression (gzip) in backend/src/main.py FastAPI middleware

### Security

- [X] T097 Verify .env files are in .gitignore and no secrets are committed to repository
- [X] T098 Add input validation and sanitization in backend/src/api/rag.py and backend/src/api/ingest.py
- [X] T099 Configure rate limiting values in production environment to prevent abuse
- [X] T100 Review CORS configuration in backend/src/main.py to ensure only allowed origins

### Monitoring & Logging

- [X] T101 [P] Add structured logging in backend/src/main.py using Python logging module with INFO level
- [X] T102 [P] Add request/response logging middleware in backend/src/main.py for debugging
- [X] T103 [P] Add error tracking configuration placeholders in backend/src/config.py for future Sentry integration

**Checkpoint**: All features complete, tested, documented, and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - Can proceed independently
- **RAG Backend (Phase 4)**: Depends on Foundational phase completion - Can proceed in parallel with US1
- **RAG Frontend (Phase 5)**: Depends on Phase 3 (Docusaurus structure) AND Phase 4 (Backend API) completion
- **User Story 2 (Phase 6)**: Depends on Phase 3 AND Phase 5 completion (need complete site to deploy)
- **User Story 4 (Phase 7)**: Depends on Phase 6 completion (need working deployment first)
- **User Story 3 (Phase 8)**: Depends on Phase 3 completion - Can be done anytime after US1
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **RAG Chatbot (Phase 4-5)**: Can start backend after Foundational, frontend integration after US1
- **User Story 2 (P2)**: Requires US1 + RAG to have complete site to deploy
- **User Story 4 (P4)**: Requires US2 (need manual deployment working first)
- **User Story 3 (P3)**: Requires US1 (need basic site structure to customize)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006, T007 can all run in parallel

**Phase 2 (Foundational)**:
- T011, T012, T013 can run in parallel (different database clients)
- T018, T019, T020, T021 can run in parallel (different model files)

**Phase 3 (US1)**:
- T024, T025, T026, T027 can run in parallel (different module _category_.json files)
- T028, T029, T030 can run in parallel (different chapter files)

**Phase 4 (RAG Backend)**:
- T034, T035, T036, T037, T038 can run in parallel (different service files)
- T040 can run in parallel with services

**Phase 5 (RAG Frontend)**:
- T047, T048 can run in parallel (install deps + create directory)

**Phase 7 (US4)**:
- T067, T068 can run in parallel (different test workflows)

**Phase 8 (US3)**:
- T074 can run in parallel with other theme tasks

**Phase 9 (Polish)**:
- T083, T084, T085 can run in parallel (different README files)
- T086, T087 can run in parallel (different doc files)
- T091, T092, T093 can run in parallel (different test categories)
- T094, T095, T096 can run in parallel (different optimization areas)
- T101, T102, T103 can run in parallel (different logging configurations)

---

## Parallel Example: Foundational Phase

```bash
# Launch all database client files together:
Task T011: "Create backend/src/db/__init__.py"
Task T012: "Create backend/src/db/qdrant_client.py"
Task T013: "Create backend/src/db/postgres_client.py"

# Launch all Pydantic model files together:
Task T018: "Create backend/src/models/__init__.py"
Task T019: "Create backend/src/models/documents.py"
Task T020: "Create backend/src/models/queries.py"
Task T021: "Create backend/src/models/embeddings.py"
```

---

## Parallel Example: RAG Backend Services

```bash
# Launch all service files together (no dependencies between them):
Task T034: "Create backend/src/services/__init__.py"
Task T035: "Create backend/src/services/embedder.py"
Task T036: "Create backend/src/services/retriever.py"
Task T037: "Create backend/src/services/generator.py"
Task T038: "Create backend/src/services/citation_extractor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T021) - CRITICAL
3. Complete Phase 3: User Story 1 (T022-T033)
4. **STOP and VALIDATE**: Test User Story 1 independently - authors can write and preview content locally
5. This is the minimum viable product for content authoring

### Incremental Delivery with RAG

1. Complete Setup + Foundational → Foundation ready
2. Complete User Story 1 → Test independently → Authors can write content (MVP!)
3. Complete RAG Backend (Phase 4) → Test API independently
4. Complete RAG Frontend (Phase 5) → Test chatbot independently
5. Complete User Story 2 → Deploy to GitHub Pages → Public access (Public MVP!)
6. Complete User Story 4 → Automated deployment working
7. Complete User Story 3 → Professional branding applied
8. Complete Polish → Production-ready

### Parallel Team Strategy

With 2-3 developers after Foundational phase completes:

1. **Developer A**: User Story 1 (Docusaurus content structure)
2. **Developer B**: RAG Backend (FastAPI services and endpoints)
3. **Developer C**: User Story 3 (Theme customization - can start after A completes)

Then merge:
4. **Developer A+B**: RAG Frontend Integration (needs both Docusaurus and backend)
5. **Developer A**: User Story 2 (Deployment)
6. **Developer A**: User Story 4 (CI/CD)
7. **All**: Phase 9 (Polish and testing)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
  - [US1] = User Story 1 (P1) - Author Content Creation
  - [US2] = User Story 2 (P2) - Public Access
  - [US3] = User Story 3 (P3) - Theme Customization
  - [US4] = User Story 4 (P4) - CI/CD Pipeline
  - [RAG] = RAG Chatbot Implementation (embedded across multiple phases)
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- RAG chatbot integration spans Phases 4-5 and integrates into the overall site
- Testing is manual using quickstart.md validation procedures, no automated test suite required per spec.md
- Backend deployment to production hosting (Render, Railway, Fly.io) is documented in quickstart.md but not included as tasks (deployment configuration is environment-specific)

---

## Task Count Summary

- **Total Tasks**: 103
- **Phase 1 (Setup)**: 7 tasks (5 parallelizable)
- **Phase 2 (Foundational)**: 14 tasks (8 parallelizable)
- **Phase 3 (US1 - Docusaurus)**: 12 tasks (7 parallelizable)
- **Phase 4 (RAG Backend)**: 13 tasks (5 parallelizable)
- **Phase 5 (RAG Frontend)**: 12 tasks (2 parallelizable)
- **Phase 6 (US2 - Deployment)**: 6 tasks
- **Phase 7 (US4 - CI/CD)**: 9 tasks (2 parallelizable)
- **Phase 8 (US3 - Theme)**: 9 tasks (1 parallelizable)
- **Phase 9 (Polish)**: 21 tasks (16 parallelizable)

**Parallelization Summary**: 46 out of 103 tasks (45%) can be executed in parallel with other tasks, offering significant opportunities for concurrent development.
