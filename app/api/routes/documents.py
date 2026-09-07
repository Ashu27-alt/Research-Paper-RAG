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
from app.services.ingestion_service import ingest_document
from app.services.pdf_service import save_pdf


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
    """Upload and index a PDF.

    Args:
        file: Required PDF sent as multipart form data.
        db: Request-scoped SQLAlchemy session supplied by FastAPI.

    Returns:
        The stored document ID, filename, file path, and a success message.

    Raises:
        HTTPException: 400 for invalid input or 500 if ingestion fails.
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

    file_path = await save_pdf(file=file,)

    # -------------------------
    # 3. Extract, chunk, embed,
    #    and store document
    # -------------------------

    try:
        document = ingest_document(
            db=db,
            file_path=file_path,
            filename=file.filename,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to process the document.",
        )

    # -------------------------
    # 4. Return upload result
    # -------------------------

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "file_path": document.file_path,
        "message": "Document uploaded and processed successfully.",
    }


@router.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
):
    """List all indexed documents, newest first.

    Args:
        db: Request-scoped SQLAlchemy session.

    Returns:
        Document IDs, filenames, storage paths, and creation timestamps.
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

    return [serialize_document(document) for document in documents]


@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetailResponse,
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """Get metadata for one indexed document.

    Args:
        document_id: UUID of the document to retrieve.
        db: Request-scoped SQLAlchemy session.

    Returns:
        Document metadata plus the number of indexed chunks.

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
