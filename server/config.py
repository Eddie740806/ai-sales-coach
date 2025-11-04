"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # OpenAI配置
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"  # 使用GPT-3.5 Turbo以降低成本
    
    # 向量数据库配置
    chroma_persist_directory: str = "./chroma_db"
    
    # 数据库配置
    database_url: str = "sqlite:///./sales_coach.db"
    
    # 应用配置
    app_name: str = "AI Sales Coach Platform"
    app_version: str = "1.0.0"
    
    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

