"""SQLAlchemy models for uploaded documents and their vectorized chunks."""

import uuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Document(Base):
    """An uploaded file and its collection of indexed chunks.

    Attributes:
        id: UUID primary key generated for the document.
        filename: Original name supplied during upload.
        file_path: Local path where the PDF was saved.
        created_at: Database-generated upload timestamp.
        chunks: Related ``DocumentChunk`` rows; deleting this document deletes them.
    """

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    filename = Column(Text, nullable=False)

    file_path = Column(Text, nullable=False)
    
    processing_status = Column(
        Text,
        nullable=False,
        default="pending",
        server_default="pending",
    )


    created_at = Column(DateTime, server_default=func.now())

    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):
    """A searchable section of a document with its vector embedding.

    Attributes:
        id: Integer primary key.
        document_id: UUID of the parent document.
        page_number: One-based PDF page containing the chunk.
        chunk_index: Position of the chunk within its page.
        text: Extracted text sent to retrieval and answer generation.
        embedding: Normalized 384-dimensional vector used for similarity search.
        document: Related parent ``Document``.
    """

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )

    page_number = Column(Integer, nullable=False)

    chunk_index = Column(Integer, nullable=False)

    text = Column(Text, nullable=False)

    embedding = Column(Vector(384), nullable=False)

    document = relationship("Document", back_populates="chunks")
