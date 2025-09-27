# ============================================================================
# FILE: config/settings.py (UPDATE)
# ============================================================================
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Required
    PERPLEXITY_API_KEY: str
    OPENROUTER_API_KEY: str
    
    # Optional
    YOUTUBE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    
    # Model Configuration
    PERPLEXITY_MODEL: str = "sonar-pro"
    MAX_TOKENS: int = 2000
    
    class Config:
        env_file = '.env'
        case_sensitive = True

# Global settings instance
settings = Settings()