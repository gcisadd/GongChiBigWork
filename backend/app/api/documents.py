"""
文档管理相关 API 路由

提供文档的增删改查功能
"""

from datetime import datetime
from typing import List, Optional

import httpx
import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.api.websocket import manager
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
    summary: Optional[str] = None
    creator_id: int
    creator_name: str
    created_at: datetime
    modified_time: datetime

    class Config:
        from_attributes = True


class AISummaryRequest(BaseModel):
    """
    AI 概括请求模型
    """
    content: str


class AISummaryResponse(BaseModel):
    """
    AI 概括响应模型
    """
    summary: str


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
    print(f"[API] 更新文档请求: document_id={document_id}, user={current_user.username}")
    print(f"[API] document_data: {document_data}")
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    
    # 协作编辑：允许任何登录用户编辑文档
    # （如果是协作文档，任何登录用户都可以编辑）
    # 注意：如果需要更严格的权限控制，可以添加检查
    
    # 更新文档信息
    if document_data.title is not None:
        document.title = document_data.title
    if document_data.content is not None:
        document.content = document_data.content
    
    document.modified_time = datetime.utcnow()
    
    db.commit()
    db.refresh(document)

    # 广播文档保存消息给协作用户（添加异常处理，避免广播失败影响文档保存）
    try:
        await manager.broadcast_document_saved(
            document_id,
            current_user.username,
            document.title
        )
    except Exception as e:
        print(f"[API] 广播文档保存消息失败: {e}")
        # 忽略广播失败，不影响文档保存
    
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


# ==================== AI 概括相关 API ====================

@router.post("/ai-summary", response_model=AISummaryResponse)
async def generate_ai_summary(
    request: AISummaryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI 概括文档内容
    
    @input request - 包含文档内容的请求
    @input current_user - 当前登录用户
    @process 1. 调用 AI 接口生成概括
    #          2. 返回概括结果
    @output 返回 AI 生成的概括内容
    """
    from app.core.config import settings
    
    if not request.content or not request.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文档内容为空，无法生成概括",
        )
    
    # 构建 AI 请求
    provider = settings.AI_PROVIDER
    api_key = settings.AI_API_KEY
    api_base = settings.AI_API_BASE_URL
    model = settings.AI_MODEL
    
    # 调试日志
    print(f"[AI] Provider: {provider}, Base URL: {api_base}, Model: {model}")
    print(f"[AI] API Key present: {bool(api_key)}")
    
    # 清理 HTML 内容，只保留文本
    text_content = re.sub(r'<[^>]+>', '', request.content)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    # 限制内容长度，避免超出 token 限制
    max_length = 4000
    if len(text_content) > max_length:
        text_content = text_content[:max_length] + "..."
    
    # 构建 prompt
    prompt = f"""请用简洁的语言概括以下文档内容，要求：
1. 提取关键信息
2. 长度控制在100-200字
3. 使用中文
4. 直接输出概括内容，不要添加任何前缀或解释

文档内容：
{text_content}"""
    
    try:
        summary = ""
        
        # 方案1: Ollama 本地模型（推荐，无需 API Key）
        if provider == "ollama":
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model or "llama3.2",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 500,
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama 返回错误: {response.status_code} - {response.text[:200]}")
                
                result = response.json()
                summary = result.get("response", "").strip()
        
        # 方案2: OpenAI 兼容 API（需要 API Key）
        elif provider in ["openai", "custom", "deepseek", "qianwen", "anthropic", "google"]:
            if not api_key:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI 服务未配置，请在 .env 文件中配置 AI_API_KEY",
                )
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500,
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"AI 服务返回错误: {response.status_code} - {response.text[:200]}",
                    )
                
                result = response.json()
                if "choices" not in result or len(result["choices"]) == 0:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="AI 服务返回格式错误",
                    )
                summary = result["choices"][0]["message"]["content"]
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的 AI 提供商: {provider}，支持的选项: ollama, openai, custom, deepseek, qianwen",
            )
        
        if not summary:
            raise Exception("AI 返回内容为空")
        
        return {"summary": summary}
        
    except httpx.ConnectError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="无法连接到 AI 服务，请确保 Ollama 已启动（运行 'ollama serve'）",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI 服务请求超时，请稍后重试",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 概括失败: {str(e)}",
        )


@router.put("/{document_id}/summary", response_model=DocumentResponse)
async def update_document_summary(
    document_id: int,
    summary_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新文档的 AI 概括
    
    @input document_id - 文档ID
    @input summary_data - 包含 summary 的字典
    @input db - 数据库会话
    @input current_user - 当前登录用户
    @output 返回更新后的文档
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在",
        )
    
    # 更新概括内容
    if "summary" in summary_data:
        document.summary = summary_data["summary"]
    
    document.modified_time = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return document
