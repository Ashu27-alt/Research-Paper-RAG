"""Application entry point that registers the HTTP API routes."""

from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.api.routes.chat import router as chat_router


app = FastAPI(
    title="AI Document Intelligence API",
    description="RAG-based document question answering system",
    version="1.0.0",
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
