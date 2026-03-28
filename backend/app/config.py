"""
Application configuration using Pydantic Settings.
"""

from pathlib import Path
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Campaign Analytics API")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: Literal["development", "staging", "production"] = Field(
        default="development"
    )

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"]
    )
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])

    # File upload
    max_upload_size_mb: int = Field(default=10)
    allowed_extensions: list[str] = Field(default=[".csv"])
    upload_dir: str = Field(default="storage/uploads")

    # Persistence
    storage_dir: str = Field(default="storage")
    models_dir: str = Field(default="storage/models")
    metadata_dir: str = Field(default="storage/metadata")

    # ML Model
    default_model_type: str = Field(default="ols")
    default_test_size: float = Field(default=0.2)
    default_cv_folds: int = Field(default=5)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: Literal["json", "console"] = Field(default="console")

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert max upload size to bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Get upload directory path."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def models_path(self) -> Path:
        """Get models directory path."""
        path = Path(self.models_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def metadata_path(self) -> Path:
        """Get metadata directory path."""
        path = Path(self.metadata_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
