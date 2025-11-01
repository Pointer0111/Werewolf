"""
应用配置
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用配置
    PROJECT_NAME: str = "狼人杀游戏系统"
    VERSION: str = "1.0.0"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost/werewolf"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

