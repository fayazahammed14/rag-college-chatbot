from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Supabase Configuration
    SUPABASE_URL: str = "https://your-project-ref.supabase.co"
    SUPABASE_KEY: str = "your-supabase-service-role-key-here"
    SUPABASE_ANON_KEY: Optional[str] = "your-supabase-anon-key-here"

    # Google Gemini Configuration
    GEMINI_API_KEY: str = "your-google-gemini-api-key-here"
    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # Application Settings
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"

    # RAG Settings
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K_CHUNKS: int = 5
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
