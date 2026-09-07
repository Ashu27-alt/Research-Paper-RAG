"""FastAPI dependencies shared by database-backed routes."""

from app.db.database import SessionLocal


def get_db():
    """Yield one database session per request and close it afterwards.

    Yields:
        A SQLAlchemy session bound to the configured database engine.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
