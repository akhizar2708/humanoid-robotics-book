<!--
Sync Impact Report:
- Version: 1.0.0 (initial ratification)
- Principles added: 7 core principles for AI-driven technical book with RAG chatbot
- Sections added: Technical Stack, Development Workflow, Governance
- Templates requiring updates:
  ✅ spec-template.md - aligned with content standards
  ✅ plan-template.md - aligned with technical constraints
  ✅ tasks-template.md - aligned with deliverables structure
  ⚠ Follow-up: Verify all slash commands reference constitution correctly
-->

# AI-Driven Technical Book with Embedded RAG Chatbot Constitution

## Core Principles

### I. Spec-First Reproducible Development

Every feature MUST begin with a complete specification before implementation. All development steps MUST be documented and reproducible by another developer following the same specification. No undocumented assumptions or implicit knowledge dependencies are permitted.

**Rationale**: Reproducibility ensures knowledge transfer, debugging efficiency, and long-term maintainability. Spec-first development prevents scope creep and ensures all stakeholders understand what will be built before resources are committed.

### II. Technical Accuracy from Authoritative Sources

All technical claims, code examples, and explanations MUST be verifiable against authoritative sources (official documentation, RFCs, peer-reviewed papers, or production-tested implementations). No hallucinated or assumed information is permitted. When uncertain, MUST consult external authoritative sources or flag for verification.

**Rationale**: Technical books carry professional responsibility. Inaccurate information damages reader trust and can lead to production failures. AI-generated content requires strict grounding in verified sources.

### III. Professional Developer Clarity

Content MUST target professional developers with clear, concise explanations. Writing MUST maintain Flesch-Kincaid reading grade 10-12. Technical jargon is permitted when standard in the field, but MUST be clearly defined on first use. Code examples MUST be runnable and production-aligned, not toy examples.

**Rationale**: Professional developers value their time. Clear writing and practical examples accelerate learning and adoption. Grade 10-12 maintains technical precision while ensuring accessibility.

### IV. Modular Maintainable Content

Book content MUST be organized in discrete, independently maintainable modules. Each section MUST have clear boundaries and minimal coupling to other sections. Updates to one section MUST NOT require cascading changes across multiple unrelated sections. Code examples MUST follow the same modularity principles.

**Rationale**: Technical content evolves rapidly. Modular structure enables targeted updates without full rewrites. This extends the book's useful lifespan and reduces maintenance burden.

### V. Zero Hallucination RAG Constraint

The RAG chatbot MUST answer questions strictly from retrieved book content. When retrieved context is insufficient, the chatbot MUST explicitly state "I don't have enough information in the book to answer this" rather than generating plausible-sounding but ungrounded responses. All answers MUST include explicit section-level citations to book content.

**Rationale**: Hallucination undermines the entire value proposition of a RAG system. Users trust book-grounded answers; generating ungrounded content violates that trust and defeats the purpose of retrieval augmentation.

### VI. Selected Text Query Support

The RAG chatbot MUST support two query modes: (1) global queries across entire book content, and (2) queries scoped to user-selected text. Selected-text queries MUST retrieve and answer only from the selected context, not from unrelated book sections. This MUST function correctly in the embedded Docusaurus interface.

**Rationale**: Readers often have questions about specific passages. Selected-text queries enable precise, context-aware answers without noise from unrelated content. This significantly improves user experience and answer relevance.

### VII. Free-Tier Production Viability

All infrastructure components MUST run successfully on free-tier services (Neon Serverless Postgres, Qdrant Cloud free tier). The system MUST handle expected load within free-tier limits. Documentation MUST include explicit free-tier configuration instructions. No hidden costs or premium-tier requirements are permitted.

**Rationale**: Free-tier compatibility ensures accessibility for learners and small projects. It validates that the architecture is efficient and demonstrates cost-conscious engineering practices that readers can apply to their own projects.

## Technical Stack

**Frontend**: Docusaurus (static site generator) deployed on GitHub Pages
**RAG Chatbot UI**: Embedded React component using OpenAI Agents/ChatKit
**Backend**: FastAPI (Python)
**Vector Database**: Qdrant Cloud (free tier)
**Relational Database**: Neon Serverless Postgres (free tier)
**Embedding Model**: OpenAI text-embedding-3-small or equivalent free alternative
**LLM**: OpenAI GPT-4 or GPT-3.5-turbo (with explicit grounding instructions)

All technology choices MUST be justified in an ADR when alternatives exist. Changes to core stack components require constitutional amendment.

## Development Workflow

### Content Creation

1. **Research Phase**: Identify authoritative sources for topic area. Document all sources in bibliography.
2. **Outline Phase**: Create detailed section outline with learning objectives and key concepts.
3. **Draft Phase**: Write content with inline citations to authoritative sources. All code examples MUST be tested.
4. **Review Phase**: Verify technical accuracy against sources. Run readability analysis (target FK grade 10-12). Test all code examples.
5. **Deployment Phase**: Build Docusaurus site, deploy to GitHub Pages, verify rendering.

### RAG System Implementation

1. **Ingestion Phase**: Extract book content, chunk appropriately (target 512-1024 tokens), generate embeddings, store in Qdrant.
2. **Retrieval Phase**: Implement hybrid search (vector + keyword). Test retrieval precision/recall on sample queries.
3. **Generation Phase**: Implement strict grounding prompt template. Test for hallucination on adversarial queries.
4. **Citation Phase**: Implement section-level citation extraction and display. Verify citations link correctly to book sections.
5. **Selected-Text Phase**: Implement text selection detection and scoped retrieval. Test boundary cases (partial sentences, cross-section selections).

### Quality Gates

Before any deployment, the following MUST pass:

- All code examples execute without errors
- Readability analysis confirms FK grade 10-12
- RAG system passes zero-hallucination test suite (adversarial queries with insufficient context)
- Selected-text queries function correctly on sample selections
- Free-tier resource usage confirmed within limits
- All technical claims have documented authoritative source citations

## Governance

### Amendment Procedure

Constitutional amendments require:
1. Documented rationale for change
2. Impact analysis on existing content and code
3. Migration plan for existing artifacts (specs, plans, ADRs)
4. Approval via explicit commit message: `docs: amend constitution to vX.Y.Z (<change summary>)`

### Versioning Policy

Constitution follows semantic versioning:
- **MAJOR**: Backward-incompatible changes (principle removal, redefinition of core constraints)
- **MINOR**: New principles added, material expansions to existing principles
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review

All PRs MUST include constitution compliance checklist:
- [ ] Technical claims verified against authoritative sources
- [ ] Code examples tested and runnable
- [ ] Readability grade verified (FK 10-12)
- [ ] RAG answers grounded in retrieved content with citations
- [ ] Free-tier resource limits respected
- [ ] No plagiarism or unlicensed content

Any constitution violation MUST be justified in PR description and approved by project maintainer.

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
