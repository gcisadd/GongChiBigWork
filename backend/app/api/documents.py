"""
文档管理相关 API 路由

提供文档的增删改查功能
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.database import get_db
from app.db.models import Document, User

router = APIRouter()


class DocumentCreate(BaseModel):
    """
    创建文档请求模型
    """
    title: str
    content: Optional[str] = ""


class DocumentUpdate(BaseModel):
    """
    更新文档请求模型
    """
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentResponse(BaseModel):
    """
    文档响应模型
    """
    id: int
    title: str
    content: Optional[str] = None
    creator_id: int
    creator_name: str
    created_at: datetime
    modified_time: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """
    文档列表响应模型
    """
    total: int
    items: List[DocumentResponse]


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取文档列表（分页）
    
    @input page - 页码，从 1 开始
    @input page_size - 每页数量
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @process 1. 查询文档总数
    #          2. 分页查询文档列表
    @output 返回文档列表和总数
    """
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询总数
    total = db.query(Document).count()
    
    # 分页查询文档列表
    documents = (
        db.query(Document)
        .order_by(Document.modified_time.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    return {
        "total": total,
        "items": documents,
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个文档详情
    
    @input document_id - 文档ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回文档详情，如果文档不存在则抛出异常
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    
    return document


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新文档
    
    @input document_data - 文档数据（标题和内容）
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @process 1. 创建文档记录
    #          2. 保存到数据库
    @output 返回新创建的文档
    """
    db_document = Document(
        title=document_data.title,
        content=document_data.content or "",
        creator_id=current_user.id,
        creator_name=current_user.username,
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新文档
    
    @input document_id - 文档ID
    @input document_data - 要更新的文档数据
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @process 1. 查询文档是否存在
    #          2. 检查权限（只有创建者可以修改）
    #          3. 更新文档信息
    @output 返回更新后的文档
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    
    # 检查权限：只有创建者可以修改
    if document.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此文档",
        )
    
    # 更新文档信息
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.content is not None:
        document.content = document_data.content
    
    document.modified_time = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除文档
    
    @input document_id - 文档ID
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @process 1. 查询文档是否存在
    #          2. 检查权限（只有创建者可以删除）
    #          3. 删除文档
    @output 返回 204 状态码表示删除成功
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    
    # 检查权限：只有创建者可以删除
    if document.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文档",
        )
    
    db.delete(document)
    db.commit()
    
    return None
