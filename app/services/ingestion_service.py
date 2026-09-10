"""PDF ingestion pipeline: download, extract, chunk, embed, and persist."""

import os
import tempfile

from sqlalchemy.orm import Session

from app.db.models import Document, DocumentChunk
from app.services.pdf_service import extract_text
from app.services.chunking_service import chunk_pages
from app.services.embedding_service import embedding_service
from app.services.storage_service import storage_service


def ingest_document(
    db: Session,
    document: Document,
) -> Document:
    """Process a document stored in Supabase Storage."""

    temp_path = None

    try:
        # -------------------------
        # 1. Download PDF
        # -------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temp_file:

            temp_path = temp_file.name

        storage_service.download_file(
            storage_path=document.file_path,
            destination_path=temp_path,
        )

        # -------------------------
        # 2. Extract text
        # -------------------------

        pages = extract_text(temp_path)

        # -------------------------
        # 3. Create chunks
        # -------------------------

        chunks = chunk_pages(pages)

        if not chunks:
            raise ValueError(
                "No chunks were extracted from the document"
            )

        # -------------------------
        # 4. Generate embeddings
        # -------------------------

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = embedding_service.embed_texts(
            texts
        )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings do not match"
            )

        # -------------------------
        # 5. Persist chunks
        # -------------------------

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    page_number=chunk["page_number"],
                    chunk_index=chunk["chunk_index"],
                    text=chunk["text"],
                    embedding=embedding,
                )
            )

        document.processing_status = "completed"

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()
        raise

    finally:
        # -------------------------
        # 6. Remove temporary PDF
        # -------------------------

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)