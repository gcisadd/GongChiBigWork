-- =====================================================
-- MySQL 数据表创建脚本
-- 项目名称：GongChiBigWork
-- 创建日期：2026-02-02
-- 说明：创建 users、documents、friends、friend_requests 和 document_permissions 表
-- =====================================================

-- 设置数据库为当前默认数据库
USE gongchibigwork;

-- =====================================================
-- 用户表 (users)
-- 用于存储用户注册信息和个人资料
-- =====================================================

DROP TABLE IF EXISTS document_permissions;
DROP TABLE IF EXISTS friends;
DROP TABLE IF EXISTS friend_requests;
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

    -- AI概括内容
    summary TEXT NULL COMMENT 'AI概括内容',

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
-- 好友请求表 (friend_requests)
-- 用于存储好友请求信息
-- =====================================================

CREATE TABLE friend_requests (
    -- 请求ID，主键，自增
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '请求ID',

    -- 发起用户ID，外键关联 users 表
    from_user_id INT NOT NULL COMMENT '发起用户ID',

    -- 目标用户ID，外键关联 users 表
    to_user_id INT NOT NULL COMMENT '目标用户ID',

    -- 请求状态：pending（待处理）、accepted（已接受）、rejected（已拒绝）
    status ENUM('pending', 'accepted', 'rejected') NOT NULL DEFAULT 'pending' COMMENT '请求状态',

    -- 创建时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 更新时间
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    -- 索引
    INDEX idx_friend_requests_from_user (from_user_id),
    INDEX idx_friend_requests_to_user (to_user_id),
    INDEX idx_friend_requests_status (status),

    -- 外键约束（可选）
    -- CONSTRAINT fk_fr_from_user FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
    -- CONSTRAINT fk_fr_to_user FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='好友请求表';


-- =====================================================
-- 好友关系表 (friends)
-- 用于存储双向好友关系
-- =====================================================

CREATE TABLE friends (
    -- ID，主键，自增
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',

    -- 用户ID，外键关联 users 表
    user_id INT NOT NULL COMMENT '用户ID',

    -- 好友用户ID，外键关联 users 表
    friend_id INT NOT NULL COMMENT '好友用户ID',

    -- 创建时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_friends_user_id (user_id),
    INDEX idx_friends_friend_id (friend_id),

    -- 复合唯一索引：每个用户对每个好友只能有一条记录
    UNIQUE KEY uk_user_friend (user_id, friend_id),

    -- 外键约束（可选）
    -- CONSTRAINT fk_friends_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    -- CONSTRAINT fk_friends_friend FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='好友关系表';


-- =====================================================
-- 文档权限表 (document_permissions)
-- 用于存储文档的授权信息，控制哪些用户可以访问和编辑文档
-- =====================================================

CREATE TABLE document_permissions (
    -- 权限ID，主键，自增
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '权限ID',

    -- 文档ID，外键关联 documents 表
    document_id INT NOT NULL COMMENT '文档ID',

    -- 被授权用户ID，外键关联 users 表
    user_id INT NOT NULL COMMENT '被授权用户ID',

    -- 权限级别：view（仅查看）、edit（可编辑）、owner（所有者）
    permission_level ENUM('view', 'edit', 'owner') NOT NULL COMMENT '权限级别',

    -- 授权时间
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',

    -- 授权人ID，外键关联 users 表
    granted_by INT NOT NULL COMMENT '授权人ID',

    -- 索引
    INDEX idx_permissions_document_id (document_id),
    INDEX idx_permissions_user_id (user_id),
    INDEX idx_permissions_granted_by (granted_by),

    -- 复合唯一索引：每个文档对每个用户只能有一条权限记录
    UNIQUE KEY uk_document_user (document_id, user_id),

    -- 外键约束（可选）
    -- CONSTRAINT fk_perm_document FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    -- CONSTRAINT fk_perm_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    -- CONSTRAINT fk_perm_granter FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文档权限表';


-- =====================================================
-- 验证表创建成功
-- =====================================================

-- 显示所有表
SHOW TABLES;

-- 显示 users 表结构
DESCRIBE users;

-- 显示 documents 表结构
DESCRIBE documents;

-- 显示 friend_requests 表结构
DESCRIBE friend_requests;

-- 显示 friends 表结构
DESCRIBE friends;

-- 显示 document_permissions 表结构
DESCRIBE document_permissions;

-- 显示创建成功信息
SELECT '数据表创建成功！' AS 'Status';
