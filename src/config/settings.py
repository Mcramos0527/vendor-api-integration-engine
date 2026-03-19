"""
Application configuration settings.

Loads settings from environment variables with sensible defaults.
Uses pydantic-settings for type-safe configuration.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Vendor API Integration Engine"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # API
    API_VERSION: str = "1.0.0"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Database (for production composite key persistence)
    DATABASE_URL: str = "sqlite:///./data/vendor_api.db"

    # Feature Flags
    CTO_FLAG_ENABLED: bool = False
    BATCH_PROCESSING_ENABLED: bool = False
    WEBHOOK_NOTIFICATIONS_ENABLED: bool = False

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # IDoc Generation
    IDOC_TYPE: str = "ZSDA"
    SOURCE_SYSTEM: str = "VENDOR_API"
    TARGET_SYSTEM: str = "ERP"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
