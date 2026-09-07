"""Database engine and SQLAlchemy session configuration."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


# -------------------------
# 1. Create database engine
# -------------------------

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
)


# -------------------------
# 2. Create database session
# -------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# -------------------------
# 3. Create declarative base
# -------------------------

Base = declarative_base()