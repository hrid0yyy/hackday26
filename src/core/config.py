"""Configuration settings for the application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str  # anon/public key (respects RLS)
    
    # Email Verification Settings
    REQUIRE_EMAIL_VERIFICATION: bool = False  # Set to True in production
    
    # Application Configuration
    APP_NAME: str = "Hackday FastAPI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    
    # Frontend URL for redirects
    FRONTEND_URL: str = "http://localhost:3000"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
