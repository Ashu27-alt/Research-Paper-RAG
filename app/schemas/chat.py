"""Pydantic schemas for chat requests and responses."""

from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for document question answering."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    document_id: UUID | None = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    max_distance: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
    )


class SourceResponse(BaseModel):
    """Metadata for a source used to generate an answer."""

    source: str
    document_id: UUID
    filename: str
    chunk_id: int
    page_number: int
    distance: float
    reranker_score: float


class ChatResponse(BaseModel):
    """Response returned by the document question-answering endpoint."""

    answer: str
    sources: list[SourceResponse]