"""Database engine, session factory, and declarative model base."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# PostgreSQL connection used by SQLAlchemy and pgvector.
DATABASE_URL = (
    "postgresql+psycopg://"
    "rag_user:rag_password"
    "@localhost:5432/"
    "rag_db"
)


# Shared engine that manages database connections.
engine = create_engine(
    DATABASE_URL,
    echo=True
)


# Factory for independent request or script database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Base class inherited by all SQLAlchemy ORM models.
Base = declarative_base()
