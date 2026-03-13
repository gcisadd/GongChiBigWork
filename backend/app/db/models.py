"""
数据库模型定义

定义用户、文档等数据表结构
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class FriendStatus(str, enum.Enum):
    """
    好友状态枚举
    """
    PENDING = "pending"      # 待处理（请求中）
    ACCEPTED = "accepted"    # 已接受（已经是好友）
    REJECTED = "rejected"    # 已拒绝


class PermissionLevel(str, enum.Enum):
    """
    文档权限级别枚举
    """
    VIEW = "view"        # 仅查看
    EDIT = "edit"        # 可编辑
    OWNER = "owner"      # 所有者（创建者）


class User(Base):
    """
    用户表模型

    存储用户基本信息
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    bio = Column(Text, nullable=True, comment="个人简介")
    hashed_password = Column(String(255), nullable=False, comment="加密后的密码")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 好友关系（作为发起者）
    sent_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.from_user_id", back_populates="from_user")
    # 好友关系（作为接收者）
    received_friend_requests = relationship("FriendRequest", foreign_keys="FriendRequest.to_user_id", back_populates="to_user")


class FriendRequest(Base):
    """
    好友请求表模型

    存储好友请求信息
    """
    __tablename__ = "friend_requests"

    id = Column(Integer, primary_key=True, index=True, comment="请求ID")
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发起用户ID")
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="目标用户ID")
    status = Column(SQLEnum(FriendStatus), default=FriendStatus.PENDING, nullable=False, comment="请求状态")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_friend_requests")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_friend_requests")


class Friend(Base):
    """
    好友关系表模型

    存储双向好友关系
    """
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="好友用户ID")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    # 索引，确保唯一性
    __table_args__ = (
        # 复合唯一索引：每个用户对每个好友只能有一条记录
    )


class Document(Base):
    """
    文档表模型

    存储文档信息，包括标题、富文本内容和AI概括
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    content = Column(Text, nullable=True, comment="文档内容（HTML格式）")
    summary = Column(Text, nullable=True, comment="AI概括内容")
    creator_id = Column(Integer, nullable=False, index=True, comment="创建者用户ID")
    creator_name = Column(String(50), nullable=False, comment="创建者用户名")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    modified_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="修改时间")

    # 文档权限关系
    permissions = relationship("DocumentPermission", back_populates="document", cascade="all, delete-orphan")


class DocumentPermission(Base):
    """
    文档权限表模型

    存储文档的授权信息，控制哪些用户可以访问和编辑文档
    """
    __tablename__ = "document_permissions"

    id = Column(Integer, primary_key=True, index=True, comment="权限ID")
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True, comment="文档ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="被授权用户ID")
    permission_level = Column(SQLEnum(PermissionLevel), nullable=False, comment="权限级别")
    granted_at = Column(DateTime, default=datetime.utcnow, comment="授权时间")
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="授权人ID")

    # 关系
    document = relationship("Document", back_populates="permissions")
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])

    # 复合唯一索引：每个文档对每个用户只能有一条权限记录
    __table_args__ = (
    )


class Comment(Base):
    """
    评论表模型

    存储文档的评论和回复，支持嵌套回复
    """
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, comment="评论ID")
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True, comment="文档ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="评论用户ID")
    username = Column(String(50), nullable=False, comment="评论用户名")
    content = Column(Text, nullable=False, comment="评论内容")
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True, comment="父评论ID，用于回复")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    # 关系
    document = relationship("Document")
    user = relationship("User")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
