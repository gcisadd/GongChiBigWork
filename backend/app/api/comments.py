"""
评论管理相关 API 路由

提供文档评论的创建、查询、回复、删除等功能
所有者、编辑者、查看者都可以评论和回复
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.document_permissions import check_document_access
from app.db.database import get_db
from app.db.models import Comment, Document, User

router = APIRouter()


# ==================== Request/Response Models ====================

class CommentCreate(BaseModel):
    """
    创建评论请求模型
    """
    content: str  # 评论内容


class CommentReplyCreate(BaseModel):
    """
    创建回复请求模型
    """
    content: str  # 回复内容
    parent_id: int  # 父评论ID


class CommentResponse(BaseModel):
    """
    评论响应模型
    """
    id: int
    document_id: int
    user_id: int
    username: str
    avatar: Optional[str] = None  # 用户头像（Base64）
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    # 嵌套的回复列表
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """
    评论列表响应模型
    """
    total: int
    items: List[CommentResponse]


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str


# 更新前向引用
CommentResponse.model_rebuild()


# ==================== Helper Functions ====================

def check_comment_permission(db: Session, document_id: int, user_id: int) -> bool:
    """
    检查用户是否有权限评论（所有者、编辑者、查看者都可以评论）

    @input db - 数据库会话
    @input document_id - 文档ID
    @input user_id - 用户ID
    @output 返回是否有评论权限
    """
    access_level = check_document_access(db, document_id, user_id)
    # owner, edit, view 都可以评论
    return access_level in ["owner", "edit", "view"]


def get_comment_tree(comments: List[Comment], user_avatars: dict, parent_id: Optional[int] = None) -> List[CommentResponse]:
    """
    将评论列表转换为树形结构

    @input comments - 所有评论列表
    @input user_avatars - 用户头像字典 {user_id: avatar}
    @input parent_id - 父评论ID
    @output 返回树形结构的评论列表
    """
    result = []
    for comment in comments:
        if comment.parent_id == parent_id:
            # 递归获取子评论
            replies = get_comment_tree(comments, user_avatars, comment.id)
            result.append(CommentResponse(
                id=comment.id,
                document_id=comment.document_id,
                user_id=comment.user_id,
                username=comment.username,
                avatar=user_avatars.get(comment.user_id, ""),
                content=comment.content,
                parent_id=comment.parent_id,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                replies=replies
            ))
    return result


# ==================== API Endpoints ====================

@router.get("/{document_id}/comments", response_model=CommentListResponse)
async def get_document_comments(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取文档的评论列表（树形结构）

    @input document_id - 文档ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回文档的评论列表
    """
    # 检查文档是否存在
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 检查用户是否有权限访问文档
    access_level = check_document_access(db, document_id, current_user.id)
    if access_level is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问此文档"
        )

    # 获取所有评论（按时间正序）
    comments = db.query(Comment).filter(
        Comment.document_id == document_id
    ).order_by(Comment.created_at.asc()).all()

    # 获取所有评论用户的头像
    user_ids = list(set([c.user_id for c in comments]))
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_avatars = {u.id: u.avatar or "" for u in users}

    # 转换为树形结构
    comment_tree = get_comment_tree(comments, user_avatars, None)

    return {
        "total": len(comments),
        "items": comment_tree
    }


@router.post("/{document_id}/comments", response_model=CommentResponse)
async def create_comment(
    document_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建评论

    @input document_id - 文档ID
    @input comment_data - 评论数据
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回创建的评论
    """
    # 检查文档是否存在
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 检查用户是否有评论权限（所有者、编辑者、查看者）
    if not check_comment_permission(db, document_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限评论此文档"
        )

    # 验证评论内容
    if not comment_data.content or not comment_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="评论内容不能为空"
        )

    # 创建评论
    new_comment = Comment(
        document_id=document_id,
        user_id=current_user.id,
        username=current_user.username,
        content=comment_data.content.strip(),
        parent_id=None  # 顶级评论
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return CommentResponse(
        id=new_comment.id,
        document_id=new_comment.document_id,
        user_id=new_comment.user_id,
        username=new_comment.username,
        avatar=current_user.avatar or "",
        content=new_comment.content,
        parent_id=new_comment.parent_id,
        created_at=new_comment.created_at,
        updated_at=new_comment.updated_at,
        replies=[]
    )


@router.post("/{document_id}/comments/reply", response_model=CommentResponse)
async def reply_to_comment(
    document_id: int,
    reply_data: CommentReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    回复评论

    @input document_id - 文档ID
    @input reply_data - 回复数据
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回创建的回复
    """
    # 检查文档是否存在
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 检查用户是否有评论权限
    if not check_comment_permission(db, document_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限评论此文档"
        )

    # 检查父评论是否存在
    parent_comment = db.query(Comment).filter(
        Comment.id == reply_data.parent_id,
        Comment.document_id == document_id
    ).first()
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="父评论不存在"
        )

    # 验证回复内容
    if not reply_data.content or not reply_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="回复内容不能为空"
        )

    # 创建回复
    new_reply = Comment(
        document_id=document_id,
        user_id=current_user.id,
        username=current_user.username,
        content=reply_data.content.strip(),
        parent_id=reply_data.parent_id
    )
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)

    return CommentResponse(
        id=new_reply.id,
        document_id=new_reply.document_id,
        user_id=new_reply.user_id,
        username=new_reply.username,
        avatar=current_user.avatar or "",
        content=new_reply.content,
        parent_id=new_reply.parent_id,
        created_at=new_reply.created_at,
        updated_at=new_reply.updated_at,
        replies=[]
    )


@router.delete("/{document_id}/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    document_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除评论（评论者本人可以删除）

    @input document_id - 文档ID
    @input comment_id - 评论ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 检查评论是否存在
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.document_id == document_id
    ).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    # 检查用户是否是评论者本人或文档所有者
    access_level = check_document_access(db, document_id, current_user.id)
    is_owner = access_level == "owner"
    is_commenter = comment.user_id == current_user.id

    if not is_owner and not is_commenter:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限删除此评论"
        )

    # 删除评论（级联删除子评论）
    db.delete(comment)
    db.commit()

    return {"message": "评论已删除"}


@router.put("/{document_id}/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    document_id: int,
    comment_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    编辑评论（评论者本人可以编辑）

    @input document_id - 文档ID
    @input comment_id - 评论ID
    @input comment_data - 评论数据
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回更新后的评论
    """
    # 检查评论是否存在
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.document_id == document_id
    ).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="评论不存在"
        )

    # 检查用户是否是评论者本人
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限编辑此评论"
        )

    # 验证评论内容
    if not comment_data.content or not comment_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="评论内容不能为空"
        )

    # 更新评论
    comment.content = comment_data.content.strip()
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)

    # 获取子评论
    replies = db.query(Comment).filter(
        Comment.parent_id == comment.id
    ).all()
    reply_responses = [
        CommentResponse(
            id=r.id,
            document_id=r.document_id,
            user_id=r.user_id,
            username=r.username,
            content=r.content,
            parent_id=r.parent_id,
            created_at=r.created_at,
            updated_at=r.updated_at,
            replies=[]
        ) for r in replies
    ]

    return CommentResponse(
        id=comment.id,
        document_id=comment.document_id,
        user_id=comment.user_id,
        username=comment.username,
        content=comment.content,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=reply_responses
    )
