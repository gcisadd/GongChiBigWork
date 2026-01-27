"""
认证相关 API 路由

提供用户登录、注册等功能
"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.database import get_db
from app.db.models import User

router = APIRouter()

# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserLogin(BaseModel):
    """
    用户登录请求模型
    """
    username: str
    password: str
    remember: Optional[bool] = False


class UserRegister(BaseModel):
    """
    用户注册请求模型
    """
    username: str
    password: str
    email: str
    phone: Optional[str] = None


class Token(BaseModel):
    """
    Token 响应模型
    """
    access_token: str
    token_type: str = "bearer"
    username: str


class UserResponse(BaseModel):
    """
    用户信息响应模型
    """
    id: int
    username: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    
    @input token - JWT token（从请求头中提取）
    @input db - 数据库会话
    @process 1. 解码 token 获取用户信息
    #          2. 从数据库查询用户
    @output 返回用户对象，如果 token 无效则抛出异常
    """
    from app.core.security import decode_access_token
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    @input form_data - 登录表单数据（用户名和密码）
    @input db - 数据库会话
    @process 1. 验证用户名和密码
    #          2. 生成 JWT token
    @output 返回包含 access_token 的响应
    """
    # 查询用户
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 验证用户是否存在和密码是否正确
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
    }


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    
    @input user_data - 用户注册信息
    @input db - 数据库会话
    @process 1. 检查用户名和邮箱是否已存在
    #          2. 加密密码
    #          3. 创建新用户
    @output 返回新创建的用户信息
    """
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在",
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册",
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hashed_password,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    
    @input current_user - 当前登录用户（从 token 中解析）
    @output 返回当前用户的基本信息
    """
    return current_user
