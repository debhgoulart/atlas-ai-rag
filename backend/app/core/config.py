"""Configuration settings for Atlas AI Backend using Pydantic Settings."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Information
    ENVIRONMENT: str = Field(default="development", description="Runtime environment")
    APP_NAME: str = Field(default="Atlas AI", description="Application name")
    APP_VERSION: str = Field(default="0.1.0", description="Application version")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Server Configuration
    BACKEND_HOST: str = Field(default="0.0.0.0", description="Server listen host")
    BACKEND_PORT: int = Field(default=8000, description="Server listen port")
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Allowed CORS origins for frontend communication",
    )

    # Database Configuration (PostgreSQL + pgvector)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://atlas_user:atlas_password@localhost:5432/atlas_ai_db",
        description="Async SQLAlchemy database connection URL",
    )

    # Google Gemini API Configuration
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_CHAT_MODEL: str = Field(default="gemini-2.5-flash", description="Model for conversational RAG")
    GEMINI_EMBEDDING_MODEL: str = Field(
        default="text-embedding-004", description="Official Google Gemini embedding model"
    )
    EMBEDDING_DIMENSION: int = Field(default=768, description="Vector dimension size for embeddings")

    # Document & RAG Pipeline Configuration
    DEFAULT_CHUNK_SIZE: int = Field(default=500, description="Chunk size in characters")
    DEFAULT_CHUNK_OVERLAP: int = Field(default=100, description="Chunk overlap in characters")
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, description="Maximum allowed file upload size in megabytes")

    @property
    def max_upload_size_bytes(self) -> int:
        """Calculate maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
