"""
FastAPI 主应用入口文件

提供后端 API 服务，包含用户认证、文档管理、个人信息等功能
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import auth, documents, profile, websocket, friends, document_permissions, comments
from app.core.config import settings
from app.db.database import engine
from app.db.models import Base


def _ensure_avatar_column():
    """若 users 表缺少 avatar 列则添加（兼容旧数据库，支持 SQLite 与 MySQL）"""
    with engine.connect() as conn:
        try:
            if "sqlite" in settings.DATABASE_URL:
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                if "avatar" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN avatar TEXT"))
                    conn.commit()
            elif "mysql" in settings.DATABASE_URL:
                # MySQL: 检查 information_schema
                db_name = settings.DATABASE_URL.split("/")[-1].split("?")[0]
                result = conn.execute(
                    text(
                        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                        "WHERE TABLE_SCHEMA = :db AND TABLE_NAME = 'users' AND COLUMN_NAME = 'avatar'"
                    ),
                    {"db": db_name},
                )
                if result.fetchone() is None:
                    conn.execute(text("ALTER TABLE users ADD COLUMN avatar TEXT NULL"))
                    conn.commit()
        except Exception as e:
            print(f"[启动] 检查/添加 avatar 列时出错（可忽略）: {e}")


# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)
_ensure_avatar_column()

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="GongChiBigWork 后端 API 服务",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 配置 CORS 中间件，允许前端跨域请求（包括 WebSocket）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头
)

# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档管理"])
app.include_router(profile.router, prefix="/api/profile", tags=["个人信息"])
app.include_router(friends.router, prefix="/api/friends", tags=["好友管理"])
app.include_router(document_permissions.router, prefix="/api/documents", tags=["文档权限"])
app.include_router(comments.router, prefix="/api/documents", tags=["评论管理"])
# WebSocket 路由单独注册（不需要 prefix）
app.include_router(websocket.router)


@app.get("/")
async def root():
    """
    根路径接口
    
    @output 返回 API 服务信息
    """
    return {
        "message": "GongChiBigWork API 服务",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    
    @output 返回服务健康状态
    """
    return {"status": "ok", "message": "服务运行正常"}
