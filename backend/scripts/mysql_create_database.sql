-- =====================================================
-- MySQL 数据库创建脚本
-- 项目名称：GongChiBigWork
-- 创建日期：2026-02-02
-- 说明：创建 gongchibigwork 数据库
-- =====================================================

-- 如果数据库已存在则删除（谨慎使用！）
-- DROP DATABASE IF EXISTS gongchibigwork;

-- 创建数据库，指定字符集为 utf8mb4，支持表情符号等特殊字符
CREATE DATABASE gongchibigwork
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 设置数据库为当前默认数据库
USE gongchibigwork;

-- 验证数据库创建成功
SELECT
    SCHEMA_NAME AS 'Database Name',
    DEFAULT_CHARACTER_SET_NAME AS 'Character Set',
    DEFAULT_COLLATION_NAME AS 'Collation'
FROM information_schema.SCHEMATA
WHERE SCHEMA_NAME = 'gongchibigwork';

-- 显示创建成功信息
SELECT '数据库 gongchibigwork 创建成功！' AS 'Status';
