# AI-Driven Humanoid Robotics: Technical Book with RAG Chatbot

A comprehensive technical book platform built with **Docusaurus 3.x** for content delivery and **FastAPI** for an embedded RAG (Retrieval-Augmented Generation) chatbot that answers questions about the book content.

## Overview

This project provides:
- **📚 Interactive Technical Book**: Four educational modules on humanoid robotics, ROS 2, computer vision, and AI integration
- **🤖 Embedded RAG Chatbot**: AI-powered question answering grounded in book content with section-level citations
- **🚀 Free-Tier Deployment**: Runs on GitHub Pages (frontend) + free-tier cloud services (Qdrant, Neon Postgres)
- **✨ Zero Hallucination**: Strict grounding ensures chatbot only answers from book content

## Architecture

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

## Tech Stack

**Frontend**:
- Docusaurus 3.x (React-based static site generator)
- @chatscope/chat-ui-kit-react (chatbot UI)
- MDX (Markdown + React components)

**Backend**:
- FastAPI 0.109+ (async Python web framework)
- LangChain 0.1+ (RAG orchestration)
- OpenAI API (text-embedding-3-small, GPT-3.5-turbo/GPT-4)

**Storage**:
- Qdrant Cloud (vector database, free tier 1GB)
- Neon Serverless Postgres (metadata, free tier 512MB)

## Quick Start

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.11+ and pip
- Git
- Accounts: [Qdrant Cloud](https://cloud.qdrant.io/), [Neon](https://neon.tech/), [OpenAI](https://platform.openai.com/)

### Setup (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/your-username/ai-humanoid-robotics-book.git
cd ai-humanoid-robotics-book

# 2. Install frontend dependencies
cd book
npm install

# 3. Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure environment variables
# Copy .env.example to .env and fill in your API keys
cp .env.example .env
# Edit .env with your OpenAI, Qdrant, and Neon credentials

# 5. Initialize databases
python scripts/init_qdrant.py
psql $DATABASE_URL -f scripts/init_postgres.sql

# 6. Start development servers
# Terminal 1 - Frontend:
cd book && npm start  # → http://localhost:3000

# Terminal 2 - Backend:
cd backend && uvicorn src.main:app --reload  # → http://localhost:8000
```

### Ingest Content

```bash
cd backend
python scripts/ingest_content.py --docs-dir ../book/docs
```

## Project Structure

```
.
├── book/                      # Docusaurus frontend
│   ├── docs/                  # Book content (MDX files)
│   │   ├── module-1/          # Module 1: ROS 2 Fundamentals
│   │   ├── module-2/          # Module 2: Perception & Vision
│   │   ├── module-3/          # Module 3: Motion Planning
│   │   └── module-4/          # Module 4: Integration
│   ├── src/
│   │   └── components/
│   │       └── ChatbotWidget/ # Embedded chatbot UI
│   ├── docusaurus.config.js
│   └── package.json
│
├── backend/                   # FastAPI backend
│   ├── src/
│   │   ├── api/               # REST endpoints
│   │   ├── services/          # Business logic
│   │   ├── models/            # Pydantic models
│   │   ├── db/                # Database clients
│   │   └── main.py
│   ├── scripts/               # Initialization scripts
│   ├── requirements.txt
│   └── .env.example
│
├── specs/                     # Design documentation
│   └── 001-docusaurus-infrastructure/
│       ├── spec.md            # Feature specification
│       ├── plan.md            # Architecture plan
│       ├── research.md        # Technical decisions
│       ├── data-model.md      # Database schemas
│       ├── contracts/         # API contracts (OpenAPI)
│       ├── quickstart.md      # Setup guide
│       └── tasks.md           # Implementation tasks
│
└── .github/
    └── workflows/             # CI/CD pipelines
```

## Features

### 📖 Book Content

- **Module 1**: The Robotic Nervous System (ROS 2)
- **Module 2**: Perception and Computer Vision
- **Module 3**: Motion Planning and Control
- **Module 4**: Integration and Deployment

### 🤖 RAG Chatbot

- **Global Queries**: Ask questions across the entire book
- **Selected-Text Queries**: Highlight text and ask for clarification
- **Citations**: Every answer includes section-level citations with clickable links
- **Confidence Scoring**: Low-confidence answers trigger "I don't know" responses

### 🚀 Deployment

- **Frontend**: Automated deployment to GitHub Pages via GitHub Actions
- **Backend**: Deploy to Render, Railway, or Fly.io (see [quickstart.md](specs/001-docusaurus-infrastructure/quickstart.md))

## Documentation

- **[Quick Start Guide](specs/001-docusaurus-infrastructure/quickstart.md)** - Comprehensive setup and deployment
- **[Feature Specification](specs/001-docusaurus-infrastructure/spec.md)** - User stories and requirements
- **[Implementation Plan](specs/001-docusaurus-infrastructure/plan.md)** - Architecture and technical decisions
- **[API Contracts](specs/001-docusaurus-infrastructure/contracts/)** - OpenAPI 3.0 specifications
- **[Data Model](specs/001-docusaurus-infrastructure/data-model.md)** - Database schemas

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd book
npm test
```

### Code Quality

```bash
# Backend
cd backend
black src/ tests/
flake8 src/ tests/

# Frontend
cd book
npm run lint
```

### API Documentation

When the backend is running, view interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Constitutional Principles

This project follows strict development principles:

1. **Spec-First Development**: All features defined before implementation
2. **Technical Accuracy**: Content sourced from authoritative documentation
3. **Zero Hallucination**: RAG chatbot never invents information
4. **Free-Tier Viability**: Runs on free cloud services
5. **Modular Content**: Independent modules and chapters
6. **Selected-Text Queries**: Users can ask about highlighted content
7. **Professional Clarity**: FK grade 10-12 readability

See [.specify/memory/constitution.md](.specify/memory/constitution.md) for full principles.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details

## Support

- **Issues**: [GitHub Issues](https://github.com/your-username/ai-humanoid-robotics-book/issues)
- **Documentation**: [specs/001-docusaurus-infrastructure/](specs/001-docusaurus-infrastructure/)
- **API Docs**: http://localhost:8000/docs (when backend running)

## Acknowledgments

- Built with [Docusaurus](https://docusaurus.io/) by Meta
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Vector search by [Qdrant](https://qdrant.tech/)
- Database by [Neon](https://neon.tech/)
- AI by [OpenAI](https://openai.com/)

---

**Status**: Active Development | **Version**: 1.0.0 | **Updated**: 2025-12-17
