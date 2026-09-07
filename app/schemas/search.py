"""Pydantic schemas for semantic document search."""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Query parameters accepted by the document search endpoint."""

    query: str = Field(..., min_length=1, max_length=2000)
    document_id: UUID | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    max_distance: float = Field(default=1.0, ge=0.0, le=2.0)


class SearchResultResponse(BaseModel):
    """One chunk returned by semantic search."""

    chunk_id: int
    page_number: int
    text: str
    distance: float


class SearchResponse(BaseModel):
    """Response returned by the document search endpoint."""

    query: str
    results: list[SearchResultResponse]
