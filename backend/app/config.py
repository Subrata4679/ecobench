from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ecobench"
    test_database_url: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = False
    log_level: str = "INFO"
    
    # LLM Configuration
    llm_provider: str = "tinyllama"  # tinyllama, openai, mock
    openai_api_key: Optional[str] = None
    tinyllama_model_path: str = "./models/tinyllama"
    embedding_dimension: int = 1536
    
    # File Storage
    data_dir: str = "./data"
    upload_dir: str = "./uploads"
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # External Services
    tesseract_cmd: str = "tesseract"
    
    # Frontend Configuration
    react_app_api_url: str = "http://localhost:8000"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure directories exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(f"{settings.data_dir}/reports", exist_ok=True)
os.makedirs(f"{settings.data_dir}/models", exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)
