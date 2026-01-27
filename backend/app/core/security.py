"""
安全工具模块

提供密码加密、JWT Token 生成和验证等功能
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    @input plain_password - 明文密码
    @input hashed_password - 加密后的密码
    @process 使用 bcrypt 验证密码是否匹配
    @output 返回 True 如果密码匹配，否则返回 False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    加密密码
    
    @input password - 明文密码
    @process 使用 bcrypt 加密密码
    @output 返回加密后的密码字符串
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌
    
    @input data - 要编码到 token 中的数据（通常是用户信息）
    @input expires_delta - token 过期时间增量（可选）
    @process 1. 设置过期时间
    #          2. 将数据编码为 JWT token
    @output 返回 JWT token 字符串
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT 访问令牌
    
    @input token - JWT token 字符串
    @process 1. 验证 token 签名和过期时间
    #          2. 解码 token 数据
    @output 返回解码后的数据字典，如果 token 无效则返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
