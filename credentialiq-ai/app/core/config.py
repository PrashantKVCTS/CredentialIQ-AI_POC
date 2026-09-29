"""Application configuration settings using pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "CredentialIQ AI POC"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./credentialiq.db"

    # LLM Settings
    LLM_PROVIDER: str = "deterministic"  # "deterministic" or "gemini"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_TIMEOUT_SECONDS: float = 10.0

    # Knowledge Base
    KNOWLEDGE_BASE_DIR: str = "./knowledge"

    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def knowledge_path(self) -> Path:
        """Absolute path to knowledge repository directory."""
        return Path(self.KNOWLEDGE_BASE_DIR).resolve()


settings = Settings()
