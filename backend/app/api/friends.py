"""
好友系统相关 API 路由

提供好友管理、好友请求等功能
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.auth import get_current_user
from app.db.database import get_db
from app.db.models import User, FriendRequest, Friend, FriendStatus

router = APIRouter()


# ==================== Request/Response Models ====================

class FriendRequestCreate(BaseModel):
    """
    发送好友请求请求模型
    """
    username: str  # 目标用户的用户名


class FriendRequestResponse(BaseModel):
    """
    好友请求响应模型
    """
    id: int
    from_user_id: int
    from_username: str
    to_user_id: int
    to_username: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class FriendResponse(BaseModel):
    """
    好友响应模型
    """
    id: int
    friend_id: int
    friend_username: str
    friend_email: str
    created_at: datetime

    class Config:
        from_attributes = True


class FriendListResponse(BaseModel):
    """
    好友列表响应模型
    """
    total: int
    items: List[FriendResponse]


class FriendRequestListResponse(BaseModel):
    """
    好友请求列表响应模型
    """
    total: int
    items: List[FriendRequestResponse]


class UserSearchResponse(BaseModel):
    """
    用户搜索响应模型
    """
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str


# ==================== Helper Functions ====================

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()


def get_friendship(db: Session, user_id: int, friend_id: int) -> Optional[Friend]:
    """检查两个用户是否是好友关系"""
    return db.query(Friend).filter(
        Friend.user_id == user_id,
        Friend.friend_id == friend_id
    ).first()


def get_pending_request(db: Session, from_user_id: int, to_user_id: int) -> Optional[FriendRequest]:
    """检查是否存在待处理的好友请求"""
    return db.query(FriendRequest).filter(
        FriendRequest.from_user_id == from_user_id,
        FriendRequest.to_user_id == to_user_id,
        FriendRequest.status == FriendStatus.PENDING
    ).first()


# ==================== API Endpoints ====================

@router.get("/search", response_model=List[UserSearchResponse])
async def search_users(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    搜索用户

    @input q - 搜索关键词（用户名或邮箱）
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回匹配的用户列表
    """
    # 限制搜索结果数量
    limit = 20

    # 模糊搜索用户名或邮箱
    users = db.query(User).filter(
        User.id != current_user.id,  # 排除自己
        or_(
            User.username.contains(q),
            User.email.contains(q)
        )
    ).limit(limit).all()

    return users


@router.get("/friends", response_model=FriendListResponse)
async def get_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的好友列表

    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回好友列表
    """
    # 查询当前用户的所有好友
    friends = db.query(Friend).filter(Friend.user_id == current_user.id).all()

    # 获取好友详细信息
    result = []
    for friend in friends:
        friend_user = db.query(User).filter(User.id == friend.friend_id).first()
        if friend_user:
            result.append(FriendResponse(
                id=friend.id,
                friend_id=friend_user.id,
                friend_username=friend_user.username,
                friend_email=friend_user.email,
                created_at=friend.created_at
            ))

    return {
        "total": len(result),
        "items": result
    }


@router.get("/requests/received", response_model=FriendRequestListResponse)
async def get_received_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取收到的好友请求列表

    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回收到的好友请求列表
    """
    requests = db.query(FriendRequest).filter(
        FriendRequest.to_user_id == current_user.id,
        FriendRequest.status == FriendStatus.PENDING
    ).order_by(FriendRequest.created_at.desc()).all()

    result = []
    for req in requests:
        from_user = db.query(User).filter(User.id == req.from_user_id).first()
        to_user = db.query(User).filter(User.id == req.to_user_id).first()
        if from_user and to_user:
            result.append(FriendRequestResponse(
                id=req.id,
                from_user_id=from_user.id,
                from_username=from_user.username,
                to_user_id=to_user.id,
                to_username=to_user.username,
                status=req.status.value,
                created_at=req.created_at
            ))

    return {
        "total": len(result),
        "items": result
    }


@router.get("/requests/sent", response_model=FriendRequestListResponse)
async def get_sent_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取发送的好友请求列表

    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回发送的好友请求列表
    """
    requests = db.query(FriendRequest).filter(
        FriendRequest.from_user_id == current_user.id,
        FriendRequest.status == FriendStatus.PENDING
    ).order_by(FriendRequest.created_at.desc()).all()

    result = []
    for req in requests:
        from_user = db.query(User).filter(User.id == req.from_user_id).first()
        to_user = db.query(User).filter(User.id == req.to_user_id).first()
        if from_user and to_user:
            result.append(FriendRequestResponse(
                id=req.id,
                from_user_id=from_user.id,
                from_username=from_user.username,
                to_user_id=to_user.id,
                to_username=to_user.username,
                status=req.status.value,
                created_at=req.created_at
            ))

    return {
        "total": len(result),
        "items": result
    }


@router.post("/request", response_model=MessageResponse)
async def send_friend_request(
    request: FriendRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    发送好友请求

    @input request - 包含目标用户名的请求
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 查找目标用户
    target_user = get_user_by_username(db, request.username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不能添加自己为好友
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能添加自己为好友"
        )

    # 检查是否已经是好友
    if get_friendship(db, current_user.id, target_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="你们已经是好友了"
        )

    # 检查是否已有待处理的请求
    # 检查当前用户发给目标用户的请求
    existing_request = get_pending_request(db, current_user.id, target_user.id)
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已发送过好友请求，请等待对方确认"
        )

    # 检查是否有反向的待处理请求（对方发给我的请求）
    reverse_request = get_pending_request(db, target_user.id, current_user.id)
    if reverse_request:
        # 自动成为好友
        reverse_request.status = FriendStatus.ACCEPTED

        # 创建双向好友关系
        friend1 = Friend(user_id=current_user.id, friend_id=target_user.id)
        friend2 = Friend(user_id=target_user.id, friend_id=current_user.id)
        db.add(friend1)
        db.add(friend2)
        db.commit()

        return {"message": "你们已经成为好友了！"}

    # 创建新的好友请求
    new_request = FriendRequest(
        from_user_id=current_user.id,
        to_user_id=target_user.id,
        status=FriendStatus.PENDING
    )
    db.add(new_request)
    db.commit()

    return {"message": "好友请求已发送"}


@router.post("/request/{request_id}/accept", response_model=MessageResponse)
async def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    接受好友请求

    @input request_id - 好友请求ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 查找好友请求
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.to_user_id == current_user.id
    ).first()

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友请求不存在"
        )

    if friend_request.status != FriendStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该请求已经被处理"
        )

    # 更新请求状态
    friend_request.status = FriendStatus.ACCEPTED
    friend_request.updated_at = datetime.utcnow()

    # 获取发起请求的用户
    from_user = db.query(User).filter(User.id == friend_request.from_user_id).first()

    # 创建双向好友关系
    friend1 = Friend(user_id=current_user.id, friend_id=from_user.id)
    friend2 = Friend(user_id=from_user.id, friend_id=current_user.id)
    db.add(friend1)
    db.add(friend2)
    db.commit()

    return {"message": "你们已经成为好友了！"}


@router.post("/request/{request_id}/reject", response_model=MessageResponse)
async def reject_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    拒绝好友请求

    @input request_id - 好友请求ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 查找好友请求
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.to_user_id == current_user.id
    ).first()

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友请求不存在"
        )

    if friend_request.status != FriendStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该请求已经被处理"
        )

    # 更新请求状态
    friend_request.status = FriendStatus.REJECTED
    friend_request.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "已拒绝好友请求"}


@router.delete("/friend/{friend_id}", response_model=MessageResponse)
async def remove_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除好友

    @input friend_id - 好友ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 查找好友关系（双向）
    friend1 = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == friend_id
    ).first()

    friend2 = db.query(Friend).filter(
        Friend.user_id == friend_id,
        Friend.friend_id == current_user.id
    ).first()

    if not friend1 or not friend2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友关系不存在"
        )

    # 删除双向好友关系
    db.delete(friend1)
    db.delete(friend2)
    db.commit()

    return {"message": "已删除好友"}


@router.delete("/request/{request_id}", response_model=MessageResponse)
async def cancel_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消发送的好友请求

    @input request_id - 好友请求ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 查找好友请求
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.from_user_id == current_user.id,
        FriendRequest.status == FriendStatus.PENDING
    ).first()

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="好友请求不存在或无法取消"
        )

    # 删除好友请求
    db.delete(friend_request)
    db.commit()

    return {"message": "已取消好友请求"}
