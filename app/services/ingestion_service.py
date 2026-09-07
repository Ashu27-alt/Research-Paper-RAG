"""PDF ingestion pipeline: extract text, chunk it, embed it, and persist it."""

from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.services.pdf_service import extract_text
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embedding_service


def ingest_document(
    db: Session,
    file_path: str,
    filename: str,
) -> Document:
    """Create an indexed document from a saved PDF.

    Args:
        db: Active SQLAlchemy session used for all persistence.
        file_path: Local path to the PDF that should be ingested.
        filename: Original file name stored with the document record.

    Returns:
        The committed ``Document`` ORM object.

    Raises:
        ValueError: If the PDF yields no chunks or embedding counts disagree.
        Exception: Any extraction, embedding, or database error after rollback.
    """

    try:
        # Extract PDF
        pages = extract_text(file_path)

        # Chunk document
        chunks = chunk_pages(pages)

        if not chunks:
            raise ValueError(
                "No chunks were extracted from the document"
            )

        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]

        embeddings = embedding_service.embed_texts(texts)

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings do not match"
            )

        # Create document
        document = Document(
            filename=filename,
            file_path=file_path,
        )

        db.add(document)
        db.flush()

        # Store chunks + embeddings
        for chunk, embedding in zip(chunks, embeddings):

            document_chunk = DocumentChunk(
                document_id=document.id,
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
                text=chunk["text"],
                embedding=embedding,
            )

            db.add(document_chunk)

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise

if __name__ == "__main__":
    from app.db.database import SessionLocal

    pdf_path = "uploads/imageMAE.pdf"

    db = SessionLocal()

    try:
        document = ingest_document(
            db=db,
            file_path=pdf_path,
            filename="your_filename.pdf",
        )

        print("Document ID:", document.id)
        print("Filename:", document.filename)

    finally:
        db.close()
