"""
Configuration Settings for Cognition Engine API

Centralized configuration management using Pydantic settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden with environment variables.
    """

    # ===== API CONFIGURATION =====
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    reload: bool = False

    # ===== DATABASE CONFIGURATION =====
    supabase_url: str
    supabase_anon_key: str
    database_url: Optional[str] = None

    # ===== OPENAI CONFIGURATION =====
    openai_api_key: str
    openai_model: str = "text-embedding-3-small"
    openai_max_tokens: int = 500

    # ===== VECTOR DATABASE CONFIGURATION =====
    vector_db_type: str = "chromadb"  # chromadb, pinecone, weaviate
    vector_db_url: str = "./chroma_db"
    vector_db_persist: bool = True

    # ===== API KEY CONFIGURATION =====
    master_api_key: str  # For admin operations
    default_rate_limit: int = 1000  # requests per hour

    # ===== SECURITY CONFIGURATION =====
    cors_origins: str = "*"  # Comma-separated list of allowed origins
    request_timeout: int = 30  # seconds
    max_request_size: int = 10485760  # 10MB

    # ===== LOGGING CONFIGURATION =====
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None

    # ===== MONITORING CONFIGURATION =====
    sentry_dsn: Optional[str] = None
    enable_metrics: bool = True
    metrics_port: int = 9090

    # ===== BILLING CONFIGURATION =====
    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    billing_enabled: bool = False

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in environment


# Global settings instance
settings = Settings()


def get_cors_origins() -> list:
    """Parse CORS origins from settings"""
    if settings.cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in settings.cors_origins.split(",")]


def is_production() -> bool:
    """Check if running in production environment"""
    return not settings.debug and settings.api_host != "localhost"


def get_log_config() -> dict:
    """Get logging configuration"""
    return {
        "level": settings.log_level,
        "format": settings.log_format,
        "file": settings.log_file
    }
