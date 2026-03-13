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

    所有字段都是可选的，支持部分更新
    """
    username: str = None
    email: EmailStr = None
    phone: str = None
    bio: str = None
    avatar: str = None


class AvatarUpdate(BaseModel):
    """
    更新头像请求模型
    """
    avatar: str  # Base64编码的头像数据


class ProfileResponse(BaseModel):
    """
    个人信息响应模型
    """
    id: int
    username: str
    email: str
    phone: str
    bio: str
    avatar: str = None

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
        "avatar": current_user.avatar or "",
    }


@router.get("/by-username/{username}/avatar")
async def get_user_avatar_by_username(
    username: str,
    db: Session = Depends(get_db)
):
    """
    根据用户名获取用户头像（用于协作编辑等场景展示）

    @input username - 用户名
    @input db - 数据库会话
    @output 返回头像数据（Base64或空）
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"avatar": user.avatar or ""}


@router.get("/{user_id}/avatar")
async def get_user_avatar(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定用户的头像

    @input user_id - 用户ID
    @input db - 数据库会话
    @output 返回头像数据（Base64或空）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return {"avatar": user.avatar or ""}


@router.post("/avatar", response_model=dict)
async def upload_avatar(
    avatar_data: AvatarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    上传/更新当前用户头像

    @input avatar_data - 头像数据（Base64编码）
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果
    """
    current_user.avatar = avatar_data.avatar
    db.commit()
    db.refresh(current_user)

    return {"message": "头像更新成功", "avatar": current_user.avatar}


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户个人信息
    
    @input profile_data - 要更新的个人信息（可选字段）
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @process 1. 检查用户名是否与其他用户冲突（如果提供）
    #          2. 检查邮箱是否与其他用户冲突（如果提供）
    #          3. 更新用户信息（只更新提供的字段）
    @output 返回更新后的个人信息
    """
    # 检查用户名是否与其他用户冲突（如果提供了新用户名且与当前不同）
    if profile_data.username and profile_data.username != current_user.username:
        existing_user = db.query(User).filter(User.username == profile_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已被使用",
            )
        current_user.username = profile_data.username
    
    # 检查邮箱是否与其他用户冲突（如果提供了新邮箱且与当前不同）
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == profile_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册",
            )
        current_user.email = profile_data.email
    
    # 更新其他字段（如果提供）
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.avatar is not None:
        current_user.avatar = profile_data.avatar

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "phone": current_user.phone or "",
        "bio": current_user.bio or "",
        "avatar": current_user.avatar or "",
    }
