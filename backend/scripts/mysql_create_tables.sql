-- =====================================================
-- MySQL 数据表创建脚本
-- 项目名称：GongChiBigWork
-- 创建日期：2026-02-02
-- 说明：创建 users 和 documents 表
-- =====================================================

-- 设置数据库为当前默认数据库
USE gongchibigwork;

-- =====================================================
-- 用户表 (users)
-- 用于存储用户注册信息和个人资料
-- =====================================================

DROP TABLE IF EXISTS documents;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    -- 用户ID，主键，自增
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    
    -- 用户名，唯一索引，用于登录
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    
    -- 邮箱，唯一索引，用于找回密码等
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    
    -- 手机号，可为空
    phone VARCHAR(20) NULL COMMENT '手机号',
    
    -- 个人简介，可为空
    bio TEXT NULL COMMENT '个人简介',
    
    -- 加密后的密码，使用 bcrypt 加密
    hashed_password VARCHAR(255) NOT NULL COMMENT '加密后的密码',
    
    -- 创建时间，默认当前时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 更新时间，更新时自动更新
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 为常用查询字段创建索引
    INDEX idx_users_username (username),
    INDEX idx_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- =====================================================
-- 文档表 (documents)
-- 用于存储用户创建的文档信息
-- =====================================================

CREATE TABLE documents (
    -- 文档ID，主键，自增
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '文档ID',
    
    -- 文档标题
    title VARCHAR(200) NOT NULL COMMENT '文档标题',
    
    -- 文档内容，HTML 格式存储富文本内容
    content TEXT NULL COMMENT '文档内容（HTML格式）',
    
    -- 创建者ID，外键关联 users 表
    creator_id INT NOT NULL COMMENT '创建者用户ID',
    
    -- 创建者用户名，用于显示
    creator_name VARCHAR(50) NOT NULL COMMENT '创建者用户名',
    
    -- 创建时间，默认当前时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 修改时间，更新时自动更新
    modified_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
    
    -- 为常用查询字段创建索引
    INDEX idx_documents_creator_id (creator_id),
    INDEX idx_documents_created_at (created_at)
    
    -- 外键约束（可选，如需启用请取消注释）
    -- CONSTRAINT fk_documents_creator
    -- FOREIGN KEY (creator_id) REFERENCES users(id)
    -- ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档表';


-- =====================================================
-- 验证表创建成功
-- =====================================================

-- 显示所有表
SHOW TABLES;

-- 显示 users 表结构
DESCRIBE users;

-- 显示 documents 表结构
DESCRIBE documents;

-- 显示创建成功信息
SELECT '数据表创建成功！' AS 'Status';
