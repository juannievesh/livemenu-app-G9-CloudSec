from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./uploads"
    
    # Worker Pool
    WORKER_POOL_SIZE: int = 4
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ENV_FILE
        case_sensitive = True
        extra="ignore" 


settings = Settings()

