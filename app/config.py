"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application-wide configuration settings."""

    # -------------------------
    # 1. Application settings
    # -------------------------

    app_name: str = "RAG Document Intelligence"
    debug: bool = True

    # -------------------------
    # 3. Redis settings
    # -------------------------

    redis_url: str = "redis://localhost:6379/0"
    
    # -------------------------
    # 2. Database settings
    # -------------------------

    database_url: str = (
        "postgresql+psycopg://"
        "rag_user:rag_password"
        "@localhost:5432/"
        "rag_db"
    )

    # -------------------------
    # 3. Redis settings
    # -------------------------

    redis_url: str = "redis://localhost:6379/0"

    # -------------------------
    # 4. Groq settings
    # -------------------------

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    # -------------------------
    # 3. Groq settings
    # -------------------------

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    # -------------------------
    # 4. File upload settings
    # -------------------------

    upload_dir: str = "uploads"
    max_file_size_mb: int = 50

    # -------------------------
    # 5. Chunking settings
    # -------------------------

    chunk_size: int = 400
    chunk_overlap: int = 80

    # -------------------------
    # 6. Retrieval settings
    # -------------------------

    retrieval_top_k: int = 20
    reranking_top_k: int = 5
    max_distance: float = 1.0

    model_config = SettingsConfigDict(
        # Resolve from this module so commands can run from any directory.
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
