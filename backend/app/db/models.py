"""
数据库模型定义

定义用户、文档等数据表结构
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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


class Document(Base):
    """
    文档表模型
    
    存储文档信息，包括标题和富文本内容
    """
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True, comment="文档ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    content = Column(Text, nullable=True, comment="文档内容（HTML格式）")
    creator_id = Column(Integer, nullable=False, index=True, comment="创建者用户ID")
    creator_name = Column(String(50), nullable=False, comment="创建者用户名")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    modified_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="修改时间")
