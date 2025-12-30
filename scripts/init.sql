-- 数据库初始化SQL脚本
-- 用于Docker Compose自动初始化数据库

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS timeros CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

-- 使用数据库
USE timeros;

-- 注意：表结构由Alembic迁移管理，这里不需要创建表

