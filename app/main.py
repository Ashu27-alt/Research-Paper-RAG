"""Application entry point that registers the HTTP API routes."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.db import models  # noqa: F401
from app.db.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create missing database tables before serving requests.

    ``create_all`` is intentionally idempotent. It covers both a fresh database
    and an existing Docker volume that was initialized before the table DDL was
    added, without altering tables that already exist.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Document Intelligence API",
    description="RAG-based document question answering system",
    version="1.0.0",
    lifespan=lifespan,
)

# Upload and document-management endpoints.
app.include_router(documents_router, tags=["Documents"])

# Search remains nested under /documents.
app.include_router(search_router, prefix="/documents", tags=["Search"])

# Question-answering endpoint.
app.include_router(chat_router, tags=["Chat"])


@app.get("/")
def root():
    """Return a lightweight health response for the API root."""
    return {"message": "RAG API is running"}

@app.get("/health")
def health_check():
    """Return the application health status."""

    return {
        "status": "healthy",
    }
