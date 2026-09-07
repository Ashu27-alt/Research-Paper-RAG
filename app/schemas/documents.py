"""Pydantic schemas for document API requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Response schema for a document."""

    document_id: UUID
    filename: str
    file_path: str
    created_at: datetime


class DocumentDetailResponse(DocumentResponse):
    """Detailed document response including chunk count."""

    chunks: int


class DeleteDocumentResponse(BaseModel):
    """Response returned after deleting a document."""

    message: str
    document_id: UUID