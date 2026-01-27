"""
个人信息相关 API 路由

提供用户个人信息的查询和更新功能
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.db.models import User

router = APIRouter()


class ProfileUpdate(BaseModel):
    """
    更新个人信息请求模型
    """
    username: str
    email: EmailStr
    phone: str
    bio: str


class ProfileResponse(BaseModel):
    """
    个人信息响应模型
    """
    id: int
    username: str
    email: str
    phone: str
    bio: str

    class Config:
        from_attributes = True


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户个人信息
    
    @input current_user - 当前登录用户（从 token 中解析）
    @output 返回当前用户的个人信息
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone or "",
        "bio": current_user.bio or "",
    }


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户个人信息
    
    @input profile_data - 要更新的个人信息
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @process 1. 检查用户名和邮箱是否与其他用户冲突
    #          2. 更新用户信息
    @output 返回更新后的个人信息
    """
    # 检查用户名是否与其他用户冲突
    if profile_data.username != current_user.username:
        existing_user = db.query(User).filter(User.username == profile_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用",
            )
    
    # 检查邮箱是否与其他用户冲突
    if profile_data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == profile_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册",
            )
    
    # 更新用户信息
    current_user.username = profile_data.username
    current_user.email = profile_data.email
    current_user.phone = profile_data.phone
    current_user.bio = profile_data.bio
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone or "",
        "bio": current_user.bio or "",
    }
