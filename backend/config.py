"""
Configuration management for AI Lead Enrichment
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    GEMINI_API_KEY: str

    # Database
    POSTGRES_USER: str = "enrichment_user"
    POSTGRES_PASSWORD: str = "enrichment_pass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "lead_enrichment"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    CHROMA_COLLECTION_NAME: str = "companies"

    # Application
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance"""
    return Settings()


# Convenience
settings = get_settings()
