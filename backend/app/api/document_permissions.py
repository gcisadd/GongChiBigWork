"""
文档权限管理相关 API 路由

提供文档权限的授予、撤销、查询等功能
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.db.models import Document, DocumentPermission, User, PermissionLevel, Friend

router = APIRouter()


# ==================== Request/Response Models ====================

class PermissionCreate(BaseModel):
    """
    创建权限请求模型
    """
    user_id: int  # 被授权用户ID
    permission_level: str  # 权限级别: "view" 或 "edit"


class PermissionUpdate(BaseModel):
    """
    更新权限请求模型
    """
    permission_level: str  # 权限级别: "view" 或 "edit"


class PermissionResponse(BaseModel):
    """
    权限响应模型
    """
    id: int
    document_id: int
    user_id: int
    username: str  # 被授权用户用户名
    permission_level: str
    granted_at: datetime
    granted_by: int

    class Config:
        from_attributes = True


class PermissionListResponse(BaseModel):
    """
    权限列表响应模型
    """
    total: int
    items: List[PermissionResponse]


class DocumentWithPermissionResponse(BaseModel):
    """
    带有权限信息的文档响应模型
    """
    id: int
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    creator_id: int
    creator_name: str
    created_at: datetime
    modified_time: datetime
    user_permission: str  # 当前用户对此文档的权限级别
    is_owner: bool  # 当前用户是否是创建者

    class Config:
        from_attributes = True


class DocumentCreateWithPermissions(BaseModel):
    """
    创建文档时同时授权请求模型
    """
    title: str
    content: Optional[str] = ""
    permissions: Optional[List[dict]] = None  # [{"user_id": 1, "permission_level": "edit"}]


class MessageResponse(BaseModel):
    """
    通用消息响应模型
    """
    message: str


# ==================== Helper Functions ====================

def get_document_permission(db: Session, document_id: int, user_id: int) -> Optional[DocumentPermission]:
    """获取用户对文档的权限"""
    return db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id,
        DocumentPermission.user_id == user_id
    ).first()


def check_document_access(db: Session, document_id: int, user_id: int) -> str:
    """
    检查用户对文档的访问权限
    返回权限级别: "owner", "edit", "view", 或 None（无权限）
    """
    # 获取文档
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return None

    # 创建者拥有所有权限
    if document.creator_id == user_id:
        return "owner"

    # 检查是否有授权权限
    permission = get_document_permission(db, document_id, user_id)
    if permission:
        return permission.permission_level.value

    return None


def get_user_friend_ids(db: Session, user_id: int) -> List[int]:
    """获取用户的所有好友ID"""
    friends = db.query(Friend).filter(Friend.user_id == user_id).all()
    return [f.friend_id for f in friends]


# ==================== API Endpoints ====================

@router.get("", response_model=List[DocumentWithPermissionResponse])
async def get_accessible_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户有权限访问的文档列表

    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回当前用户有权访问的文档列表（创建的和被授权的）
    """
    # 1. 获取用户创建的文档
    owned_documents = db.query(Document).filter(
        Document.creator_id == current_user.id
    ).all()

    # 2. 获取用户被授权的文档
    permissions = db.query(DocumentPermission).filter(
        DocumentPermission.user_id == current_user.id
    ).all()

    permission_doc_ids = [p.document_id for p in permissions]
    shared_documents = []
    if permission_doc_ids:
        shared_documents = db.query(Document).filter(
            Document.id.in_(permission_doc_ids)
        ).all()

    # 3. 合并结果
    result = []

    # 添加创建的文档
    for doc in owned_documents:
        result.append(DocumentWithPermissionResponse(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            summary=doc.summary,
            creator_id=doc.creator_id,
            creator_name=doc.creator_name,
            created_at=doc.created_at,
            modified_time=doc.modified_time,
            user_permission="owner",
            is_owner=True
        ))

    # 添加被授权的文档
    perm_dict = {p.document_id: p.permission_level.value for p in permissions}
    for doc in shared_documents:
        if doc.id not in perm_dict:
            continue
        result.append(DocumentWithPermissionResponse(
            id=doc.id,
            title=doc.title,
            content=doc.content,
            summary=doc.summary,
            creator_id=doc.creator_id,
            creator_name=doc.creator_name,
            created_at=doc.created_at,
            modified_time=doc.modified_time,
            user_permission=perm_dict[doc.id],
            is_owner=False
        ))

    # 按修改时间排序
    result.sort(key=lambda x: x.modified_time, reverse=True)

    return result


@router.get("/{document_id}/permissions", response_model=PermissionListResponse)
async def get_document_permissions(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取文档的权限列表

    @input document_id - 文档ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回文档的权限列表（只有创建者可以查看）
    """
    # 获取文档
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 只有创建者可以查看权限列表
    if document.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文档创建者可以查看权限列表"
        )

    # 获取所有权限
    permissions = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document_id
    ).all()

    # 获取用户信息
    result = []
    for perm in permissions:
        user = db.query(User).filter(User.id == perm.user_id).first()
        if user:
            result.append(PermissionResponse(
                id=perm.id,
                document_id=perm.document_id,
                user_id=user.id,
                username=user.username,
                permission_level=perm.permission_level.value,
                granted_at=perm.granted_at,
                granted_by=perm.granted_by
            ))

    return {
        "total": len(result),
        "items": result
    }


@router.post("/{document_id}/permissions", response_model=MessageResponse)
async def add_document_permission(
    document_id: int,
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    为文档添加权限

    @input document_id - 文档ID
    @input permission_data - 权限数据
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 获取文档
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 只有创建者可以添加权限
    if document.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文档创建者可以授权"
        )

    # 检查被授权用户是否存在
    target_user = db.query(User).filter(User.id == permission_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="被授权用户不存在"
        )

    # 不能授权给自己
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能授权给自己"
        )

    # 检查是否已经是好友（可选：可以设置为需要是好友才能授权）
    # friend = get_friendship(db, current_user.id, target_user.id)
    # if not friend:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="只能给好友授权"
    #     )

    # 验证权限级别
    try:
        perm_level = PermissionLevel(permission_data.permission_level)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的权限级别，必须是 'view' 或 'edit'"
        )

    # 检查是否已有权限
    existing = get_document_permission(db, document_id, target_user.id)
    if existing:
        # 更新权限
        existing.permission_level = perm_level
        existing.granted_at = datetime.utcnow()
        existing.granted_by = current_user.id
        db.commit()
        return {"message": f"已更新 {target_user.username} 的权限为 {perm_level.value}"}

    # 创建新权限
    new_permission = DocumentPermission(
        document_id=document_id,
        user_id=target_user.id,
        permission_level=perm_level,
        granted_by=current_user.id
    )
    db.add(new_permission)
    db.commit()

    return {"message": f"已授予 {target_user.username} {perm_level.value} 权限"}


@router.put("/{document_id}/permissions/{user_id}", response_model=MessageResponse)
async def update_document_permission(
    document_id: int,
    user_id: int,
    permission_data: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新文档权限

    @input document_id - 文档ID
    @input user_id - 被授权用户ID
    @input permission_data - 权限数据
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 获取文档
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 只有创建者可以修改权限
    if document.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文档创建者可以修改权限"
        )

    # 验证权限级别
    try:
        perm_level = PermissionLevel(permission_data.permission_level)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的权限级别，必须是 'view' 或 'edit'"
        )

    # 获取权限
    permission = get_document_permission(db, document_id, user_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )

    # 更新权限
    permission.permission_level = perm_level
    permission.granted_at = datetime.utcnow()
    db.commit()

    target_user = db.query(User).filter(User.id == user_id).first()
    return {"message": f"已更新 {target_user.username} 的权限为 {perm_level.value}"}


@router.delete("/{document_id}/permissions/{user_id}", response_model=MessageResponse)
async def revoke_document_permission(
    document_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    撤销文档权限

    @input document_id - 文档ID
    @input user_id - 被授权用户ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回操作结果消息
    """
    # 获取文档
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )

    # 只有创建者可以撤销权限
    if document.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有文档创建者可以撤销权限"
        )

    # 获取权限
    permission = get_document_permission(db, document_id, user_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限记录不存在"
        )

    # 删除权限
    target_user = db.query(User).filter(User.id == user_id).first()
    db.delete(permission)
    db.commit()

    return {"message": f"已撤销 {target_user.username} 的权限"}


@router.get("/{document_id}/access", response_model=dict)
async def check_document_access_level(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    检查当前用户对文档的访问权限级别

    @input document_id - 文档ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回权限级别信息
    """
    access_level = check_document_access(db, document_id, current_user.id)

    if access_level is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有权限访问此文档"
        )

    return {
        "document_id": document_id,
        "access_level": access_level,
        "can_edit": access_level in ["owner", "edit"],
        "can_view": True,
        "can_manage_permissions": access_level == "owner"
    }
