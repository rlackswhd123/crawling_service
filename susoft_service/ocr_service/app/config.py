"""Configuration Settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings"""
    
    # OCR Configuration
    ocr_engine: str = "paddle"
    use_layout: bool = False
    max_file_mb: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 3600
    
    # Authentication
    enable_auth: bool = True  # 인증 활성화 여부 (로컬 개발: false)
    auth_token: str = "SECRET"
    
    # Google Cloud (Optional)
    gcp_project: Optional[str] = None
    gcp_credentials_json: Optional[str] = None
    
    # Database (읽기 전용)
    database_url: Optional[str] = None
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

