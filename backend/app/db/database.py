"""
数据库连接配置模块

配置 SQLAlchemy 数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 验证 DATABASE_URL 是否有效
if not settings.DATABASE_URL or settings.DATABASE_URL.strip() == "":
    raise ValueError(
        "数据库连接 URL 未设置或为空！\n"
        "请确保在 .env 文件中设置了 DATABASE_URL，\n"
        "例如：DATABASE_URL=sqlite:///./app.db"
    )

# 创建数据库引擎
# SQLite 数据库文件将保存在项目根目录
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=True,  # 开发环境显示 SQL 日志，生产环境应设为 False
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    获取数据库会话
    
    @input 无
    @process 1. 创建数据库会话
              2. 使用 yield 提供会话
              3. 使用完毕后自动关闭会话
    @output 返回数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()  # 如果有异常，回滚
        raise
    finally:
        db.close()
