"""PDF ingestion pipeline: extract text, chunk it, embed it, and persist it."""

from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.services.pdf_service import extract_text
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embedding_service


def ingest_document(
    db: Session,
    document: Document,
) -> Document:
    """Process and index an existing document.

    Args:
        db: Active SQLAlchemy session used for persistence.
        document: Document record containing the saved PDF path.

    Returns:
        The completed ``Document`` ORM object.

    Raises:
        ValueError: If the PDF yields no chunks or embedding counts disagree.
        Exception: Any extraction, embedding, or database error.
    """

    try:
        # -------------------------
        # 1. Extract PDF
        # -------------------------

        pages = extract_text(document.file_path)

        # -------------------------
        # 2. Chunk document
        # -------------------------

        chunks = chunk_pages(pages)

        if not chunks:
            raise ValueError(
                "No chunks were extracted from the document"
            )

        # -------------------------
        # 3. Generate embeddings
        # -------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_service.embed_texts(texts)

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings do not match"
            )

        # -------------------------
        # 4. Store chunks
        # -------------------------

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            document_chunk = DocumentChunk(
                document_id=document.id,
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                embedding=embedding,
            )

            db.add(document_chunk)

        # -------------------------
        # 5. Mark completed
        # -------------------------

        document.processing_status = "completed"

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise