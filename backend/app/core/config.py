"""
应用配置模块

定义应用的各种配置项，包括数据库连接、JWT 密钥、CORS 设置等

支持 SQLite 和 MySQL 两种数据库：
- SQLite（默认）：DATABASE_URL = "sqlite:///./app.db"
- MySQL：DATABASE_URL = "mysql+pymysql://user:password@host:port/dbname"
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用配置类
    
    使用 pydantic-settings 管理配置，支持从环境变量读取
    """
    
    # ==================== 项目基本信息 ====================
    
    # 项目名称
    PROJECT_NAME: str = "GongChiBigWork API"
    
    # API 前缀
    API_V1_STR: str = "/api"
    
    # ==================== 数据库配置 ====================
    
    # 数据库类型：sqlite 或 mysql
    DATABASE_TYPE: str = "mysql"
    
    # 数据库连接 URL
    # SQLite 示例：sqlite:///./app.db
    # MySQL 示例：mysql+pymysql://root:password@localhost:3306/gongchibigwork
    # 如果未设置或为空，使用默认值（MySQL）
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/gongchibigwork"
    
    # MySQL 数据库配置（可选，分别配置）
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "gongchibigwork"
    
    @classmethod
    def validate_database_url(cls, url: str) -> str:
        """
        验证并修复数据库 URL 格式
        
        @input url - 数据库连接 URL
        @process 1. 检查 URL 是否为空或无效
                  2. 如果是 MySQL URL，检查是否缺少端口并添加
                  3. 返回修复后的 URL
        @output 修复后的数据库连接 URL
        """
        # 如果 URL 为空或空白，使用默认 MySQL 连接
        if not url or not isinstance(url, str) or url.strip() == "":
            return "mysql+pymysql://root:@localhost:3306/gongchibigwork"
        
        url = url.strip()
        
        # 如果是 MySQL URL，检查并修复端口
        if url.startswith("mysql"):
            # 使用正则表达式检查是否缺少端口
            # 匹配格式：mysql+pymysql://user:pass@host/dbname
            # 修复为：mysql+pymysql://user:pass@host:3306/dbname
            import re
            # 匹配 @ 后面没有 :端口 的情况
            pattern = r'(@)([^/:]+)(/)'
            match = re.search(pattern, url)
            if match and ":" not in match.group(2):
                # 缺少端口，添加默认端口 3306
                url = re.sub(pattern, r'\1\2:3306\3', url)
        
        return url
    
    # ==================== JWT 认证配置 ====================
    
    # JWT 密钥（生产环境请修改为一个复杂的随机字符串）
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    
    # JWT 算法
    ALGORITHM: str = "HS256"
    
    # Token 过期时间（分钟）
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # ==================== CORS 配置 ====================
    
    # 允许的前端地址列表（支持开发环境）
    CORS_ORIGINS: list[str] = [
        "*",  # 允许所有来源（开发环境）
    ]
    
    # ==================== AI 概括配置 ====================
    
    # AI 提供商：ollama（本地模型，推荐）、openai、custom、deepseek、qianwen
    AI_PROVIDER: str = "ollama"
    
    # AI API Key（仅 OpenAI/custom 等需要）
    AI_API_KEY: str = ""
    
    # AI API 端点（用于自定义或代理）
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    
    # 使用的模型（Ollama 用 llama3.2, mistral 等，OpenAI 用 gpt-3.5-turbo 等）
    AI_MODEL: str = "llama3.2"
    
    class Config:
        case_sensitive = True
        env_file = ".env"  # 支持从 .env 文件读取配置


# 创建全局配置实例
settings = Settings()

# 验证并修复 DATABASE_URL
settings.DATABASE_URL = Settings.validate_database_url(settings.DATABASE_URL)
