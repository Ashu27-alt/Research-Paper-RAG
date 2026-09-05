import uuid

from sqlalchemy import Column, Text, Integer, DateTime, ForeignKey

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    filename = Column(Text, nullable=False)

    file_path = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )


class DocumentChunk(Base):

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
