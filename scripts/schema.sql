-- TimerOS 数据库表结构DDL
-- 用于直接创建数据库表结构，不依赖Alembic迁移
-- 字符集：utf8mb4，排序规则：utf8mb4_general_ci

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS timeros CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- 使用数据库
USE timeros;

-- ============================================
-- 任务表 (tasks)
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID，主键，自增',
    name VARCHAR(255) NOT NULL COMMENT '任务名称，用户自定义的任务标题',
    description TEXT NOT NULL COMMENT '任务描述，用户输入的自然语言任务描述',
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型，如research_task、analysis_task、report_task',
    schedule DATETIME NOT NULL COMMENT '任务执行时间，对于周期性任务表示下次执行时间',
    cron_expression VARCHAR(100) NULL COMMENT 'Cron表达式，仅周期性任务使用，如''0 8 * * 1''表示每周一8点',
    is_recurring BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为周期性任务，TRUE表示周期性，FALSE表示一次性',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '任务状态：pending-待执行, running-执行中, completed-已完成, failed-失败, paused-已暂停',
    params JSON NULL COMMENT '任务参数，JSON格式，包含任务执行所需的具体参数',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务创建时间，UTC时间',
    updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '任务更新时间，UTC时间，每次更新时自动刷新',
    deleted_time DATETIME NULL DEFAULT NULL COMMENT '任务删除时间，UTC时间，NULL表示未删除，用于软删除',
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_schedule (schedule),
    INDEX idx_tasks_status_schedule (status, schedule),
    INDEX idx_tasks_task_type (task_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='任务表，存储用户创建的所有定时任务';

-- ============================================
-- 任务执行记录表 (task_executions)
-- ============================================
CREATE TABLE IF NOT EXISTS task_executions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '执行记录ID，主键，自增',
    task_id INT NOT NULL COMMENT '关联的任务ID，关联tasks表的id字段',
    status VARCHAR(20) NOT NULL COMMENT '执行状态：running-执行中, completed-成功, failed-失败',
    result TEXT NULL COMMENT '执行结果，JSON格式或文本格式，包含任务执行的输出内容',
    error_message TEXT NULL COMMENT '错误信息，当执行失败时记录详细的错误描述和堆栈信息',
    execution_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务执行时间，UTC时间',
    duration_seconds FLOAT NULL COMMENT '任务执行耗时，单位：秒',
    created_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间，UTC时间',
    INDEX idx_executions_task_id (task_id),
    INDEX idx_executions_execution_time (execution_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='任务执行记录表，记录每次任务执行的详细信息';

