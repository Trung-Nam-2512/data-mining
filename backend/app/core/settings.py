"""
Application Settings
"""
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "Mushroom Classification API"
    API_DESCRIPTION: str = "RESTful API for mushroom genus recognition and toxicity detection using Deep Learning"
    API_VERSION: str = "1.0.0"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    
    # Model Settings
    MODEL_AUTO_LOAD: bool = True
    MODEL_DIR: str = "../models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

