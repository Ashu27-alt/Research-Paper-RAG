"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application-wide configuration settings."""

    app_name: str = "RAG Document Intelligence"
    debug: bool = True

    database_url: str = (
        "postgresql+psycopg://"
        "rag_user:rag_password"
        "@localhost:5432/"
        "rag_db"
    )

    redis_url: str = "redis://localhost:6379/0"

    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    upload_dir: str = "uploads"
    max_file_size_mb: int = 50

    chunk_size: int = 400
    chunk_overlap: int = 80

    retrieval_top_k: int = 20
    reranking_top_k: int = 5
    max_distance: float = 1.0

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()