"""
应用配置模块

定义应用的各种配置项，包括数据库连接、JWT 密钥、CORS 设置等
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    
    使用 pydantic-settings 管理配置，支持从环境变量读取
    """
    
    # 项目名称
    PROJECT_NAME: str = "GongChiBigWork API"
    
    # API 前缀
    API_V1_STR: str = "/api"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"  # 生产环境请修改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # CORS 配置（允许的前端地址）
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite 开发服务器默认端口
        "http://localhost:3000",  # 其他可能的开发端口
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        case_sensitive = True
        env_file = ".env"  # 支持从 .env 文件读取配置


# 创建全局配置实例
settings = Settings()
