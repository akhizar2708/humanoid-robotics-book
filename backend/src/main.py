# backend/src/main.py
"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .db.qdrant_client import qdrant_client
from .db.postgres_client import postgres_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Driven Technical Book RAG API",
    description="Retrieval-Augmented Generation API for technical book Q&A",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Rate limiting middleware (simple in-memory implementation)
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Only rate limit API endpoints
        if not request.url.path.startswith("/api/v1"):
            return await call_next(request)

        # Use session_id from request body or IP address as key
        client_id = request.client.host if request.client else "unknown"

        # Clean old requests (older than 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff_time
        ]

        # Check rate limit (10 requests per minute for queries)
        if "/query" in request.url.path:
            recent_requests = [
                req_time for req_time in self.requests[client_id]
                if req_time > datetime.now() - timedelta(minutes=1)
            ]
            if len(recent_requests) >= settings.query_rate_limit:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Query rate limit exceeded. Please try again later.",
                        "details": {
                            "retry_after": 60,
                            "limit_type": "queries",
                            "current_usage": f"{len(recent_requests)} RPM"
                        }
                    }
                )

        # Track this request
        self.requests[client_id].append(datetime.now())

        response = await call_next(request)
        return response

app.add_middleware(RateLimitMiddleware)

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Verify database connections on startup."""
    logger.info("Starting up application...")

    try:
        # Test Qdrant connection
        await qdrant_client.connect()
        logger.info("✓ Connected to Qdrant")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Qdrant: {e}")

    try:
        # Test Postgres connection
        pool = await postgres_client.connect()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        logger.info("✓ Connected to Postgres")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Postgres: {e}")

    logger.info("Application startup complete")

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    logger.info("Shutting down application...")
    await qdrant_client.close()
    await postgres_client.close()
    logger.info("Application shutdown complete")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "rag-api"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI-Driven Technical Book RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Register API routers
from .api import rag, ingest

app.include_router(rag.router, prefix="/api/v1", tags=["rag"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingest"])
