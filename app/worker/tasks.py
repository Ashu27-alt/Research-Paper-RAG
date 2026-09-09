"""
Celery background tasks for document processing.
"""

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Document
from app.services.ingestion_service import ingest_document
from app.worker.celery_app import celery_app


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_document(
    self,
    document_id: str,
):
    """Process a document asynchronously.

    Args:
        document_id: UUID of the document to process.

    Returns:
        Processing result containing the document ID and status.
    """

    db: Session = SessionLocal()

    try:
        # -------------------------
        # 1. Load document
        # -------------------------

        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if document is None:
            raise ValueError(
                f"Document {document_id} not found"
            )

        # -------------------------
        # 2. Mark processing
        # -------------------------

        document.processing_status = "processing"

        db.commit()

        # -------------------------
        # 3. Run ingestion pipeline
        # -------------------------

        ingest_document(
            db=db,
            document=document,
        )

        return {
            "document_id": str(document.id),
            "status": "completed",
        }

    except Exception:
        # -------------------------
        # 4. Mark failed
        # -------------------------

        document = db.query(Document).filter(
            Document.id == document_id
        ).first()

        if document:
            document.processing_status = "failed"
            db.commit()

        raise

    finally:
        db.close()