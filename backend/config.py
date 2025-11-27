from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    google_api_key: str
    qdrant_url: str
    qdrant_api_key: str

    # RAG configuration
    collection_name: str = "ai_spec_driven_book"
    embedding_model: str = "models/text-embedding-004"
    embedding_batch_size: int = 16

    # Retrieval configuration
    top_k_default: int = 5
    score_threshold: float = 0.2

    # Chunking configuration
    chunk_size_chars: int = 1000
    chunk_overlap_chars: int = 200
    min_chunk_chars: int = 300

    # Gemini model
    llm_model: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
