"""Endpoints for uploading, listing, inspecting, and deleting documents."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.models import Document
from app.schemas.documents import (
    DeleteDocumentResponse,
    DocumentDetailResponse,
    DocumentResponse,
    UploadDocumentResponse,
)
from app.services.pdf_service import save_pdf
from app.worker.tasks import process_document


router = APIRouter()


def serialize_document(document: Document) -> dict:
    """Convert a document ORM object into the shared API response shape.

    Args:
        document: Persisted document returned by SQLAlchemy.

    Returns:
        Document fields matching ``DocumentResponse``.
    """

    return {
        "document_id": document.id,
        "filename": document.filename,
        "file_path": document.file_path,
        "processing_status": document.processing_status,
        "created_at": document.created_at,
    }


@router.post(
    "/upload",
    response_model=UploadDocumentResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a PDF and queue it for background processing.

    Args:
        file: Required PDF sent as multipart form data.
        db: Request-scoped SQLAlchemy session supplied by FastAPI.

    Returns:
        The stored document ID, filename, processing status,
        file path, and upload message.

    Raises:
        HTTPException: 400 for invalid input or 500 if saving
            the document record fails.
    """

    # -------------------------
    # 1. Validate uploaded file
    # -------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # -------------------------
    # 2. Save PDF to disk
    # -------------------------

    file_path = await save_pdf(file=file)

    # -------------------------
    # 3. Create document record
    # -------------------------

    try:
        document = Document(
            filename=file.filename,
            file_path=file_path,
            processing_status="pending",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create document record.",
        )

    # -------------------------
    # 4. Queue background task
    # -------------------------

    try:
        process_document.delay(
            str(document.id)
        )

    except Exception:
        document.processing_status = "failed"

        db.commit()

        raise HTTPException(
            status_code=500,
            detail="Failed to queue document processing.",
        )

    # -------------------------
    # 5. Return immediately
    # -------------------------

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "file_path": document.file_path,
        "processing_status": document.processing_status,
        "message": "Document uploaded and queued for processing.",
    }


@router.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
):
    """List all documents, newest first.

    Args:
        db: Request-scoped SQLAlchemy session.

    Returns:
        Document IDs, filenames, storage paths, processing statuses,
        and creation timestamps.
    """

    # -------------------------
    # 1. Fetch documents
    # -------------------------

    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    # -------------------------
    # 2. Return document list
    # -------------------------

    return [
        serialize_document(document)
        for document in documents
    ]


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetailResponse,
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """Get metadata for one document.

    Args:
        document_id: UUID of the document to retrieve.
        db: Request-scoped SQLAlchemy session.

    Returns:
        Document metadata, processing status, and chunk count.

    Raises:
        HTTPException: 404 when no document matches ``document_id``.
    """

    # -------------------------
    # 1. Find document
    # -------------------------

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # -------------------------
    # 2. Return document details
    # -------------------------

    return {
        **serialize_document(document),
        "chunks": len(document.chunks),
    }


@router.delete(
    "/documents/{document_id}",
    response_model=DeleteDocumentResponse,
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a document and its indexed chunks.

    Args:
        document_id: UUID of the document to delete.
        db: Request-scoped SQLAlchemy session.

    Returns:
        A confirmation message and the deleted document ID.

    Raises:
        HTTPException: 404 when no document matches ``document_id``.
    """

    # -------------------------
    # 1. Find document
    # -------------------------

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # -------------------------
    # 2. Delete document
    # -------------------------

    db.delete(document)
    db.commit()

    # -------------------------
    # 3. Return confirmation
    # -------------------------

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }