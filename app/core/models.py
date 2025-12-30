"""
数据模型定义模块。

定义所有数据库表的ORM模型，包括Task（任务表）和TaskExecution（任务执行记录表）。
所有模型都继承自Base，使用SQLAlchemy的声明式API。

**重要说明**：
- 本模块定义的是SQLAlchemy ORM模型，用于数据库映射和操作
- API层的数据验证和序列化使用Pydantic模型（见`app/core/schemas.py`）
- SQLAlchemy模型可以通过`from_attributes = True`自动转换为Pydantic模型
- 本模块不定义ORM关系（relationship）和索引，这些应在SQL DDL中定义
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, JSON, String, Text

from app.core.database import Base


class Task(Base):
    """
    任务表模型（SQLAlchemy ORM）。

    存储用户创建的所有定时任务，包括一次性任务和周期性任务。
    任务状态通过status字段管理，支持pending、running、completed、failed等状态。

    该模型用于数据库操作（CRUD），API层的请求和响应使用Pydantic模型
    （`TaskCreate`、`TaskUpdate`、`TaskResponse`，见`app/core/schemas.py`）。

    **字段说明**：
        id: 任务ID，主键，自增整数
        name: 任务名称，用户自定义的任务标题，最大长度255字符
        description: 任务描述，用户输入的自然语言任务描述，文本类型
        task_type: 任务类型，如research_task、analysis_task、report_task，最大长度50字符
        schedule: 任务执行时间，DateTime类型，对于周期性任务表示下次执行时间
        cron_expression: Cron表达式，仅周期性任务使用，最大长度100字符，可为空
        is_recurring: 是否为周期性任务，布尔类型，默认False
        status: 任务状态，字符串类型，可选值：pending、running、completed、failed、paused
        params: 任务参数，JSON格式，包含任务执行所需的具体参数，可为空
        created_time: 任务创建时间，DateTime类型，UTC时间，自动设置
        updated_time: 任务更新时间，DateTime类型，UTC时间，每次更新时自动刷新
        deleted_time: 任务删除时间（软删除），DateTime类型，UTC时间，NULL表示未删除

    **设计特点**：
        - 使用utf8mb4字符集，支持完整的Unicode字符
        - 时间字段使用`_time`后缀（符合项目规范）
        - 不使用物理外键约束（关系在应用层维护）
        - 不在ORM模型中定义索引和关系（在SQL DDL中定义）
        - 支持软删除（通过deleted_time字段）

    **与Pydantic模型的配合**：
        - 可以通过`TaskResponse.model_validate(task)`自动转换
        - FastAPI会自动将SQLAlchemy模型转换为Pydantic响应模型
        - 确保字段类型与Pydantic模型匹配
    """

    __tablename__ = "tasks"

    # 主键：自增整数，作为任务的唯一标识
    id = Column(
        Integer,
        primary_key=True,
        comment="任务ID，主键，自增",
    )

    # 任务基本信息
    name = Column(
        String(255),
        nullable=False,
        comment="任务名称，用户自定义的任务标题",
    )
    description = Column(
        Text,
        nullable=False,
        comment="任务描述，用户输入的自然语言任务描述",
    )
    task_type = Column(
        String(50),
        nullable=False,
        comment="任务类型，如research_task、analysis_task、report_task",
    )

    # 调度信息
    schedule = Column(
        DateTime,
        nullable=False,
        comment="任务执行时间，对于周期性任务表示下次执行时间",
    )
    cron_expression = Column(
        String(100),
        nullable=True,
        comment="Cron表达式，仅周期性任务使用，如'0 8 * * 1'表示每周一8点",
    )
    is_recurring = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否为周期性任务，True表示周期性，False表示一次性",
    )

    # 任务状态
    status = Column(
        String(20),
        default="pending",
        nullable=False,
        comment="任务状态：pending-待执行, running-执行中, completed-已完成, failed-失败, paused-已暂停",
    )

    # 任务参数（JSON格式存储）
    params = Column(
        JSON,
        nullable=True,
        comment="任务参数，JSON格式，包含任务执行所需的具体参数",
    )

    # 时间戳字段（注意使用_time后缀）
    created_time = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="任务创建时间，UTC时间",
    )
    updated_time = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="任务更新时间，UTC时间，每次更新时自动刷新",
    )

    # 软删除字段（可选）
    deleted_time = Column(
        DateTime,
        nullable=True,
        default=None,
        comment="任务删除时间，UTC时间，NULL表示未删除，用于软删除",
    )

    # 表选项
    __table_args__ = (
        # 字符集和排序规则设置
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_general_ci"},
    )


class TaskExecution(Base):
    """
    任务执行记录表模型（SQLAlchemy ORM）。

    记录每次任务执行的详细信息，包括执行结果、错误信息、执行时间等。
    用于任务执行历史追踪和问题排查。

    该模型用于数据库操作（CRUD），API层的响应使用Pydantic模型
    （`TaskExecutionResponse`，见`app/core/schemas.py`）。

    **字段说明**：
        id: 执行记录ID，主键，自增整数
        task_id: 关联的任务ID，整数类型，关联tasks表的id字段（不使用物理外键）
        status: 执行状态，字符串类型，可选值：running、completed、failed
        result: 执行结果，文本类型，JSON格式或文本格式，包含任务执行的输出内容，可为空
        error_message: 错误信息，文本类型，当执行失败时记录详细的错误描述和堆栈信息，可为空
        execution_time: 任务执行时间，DateTime类型，UTC时间，自动设置
        duration_seconds: 任务执行耗时，浮点数类型，单位：秒，可为空
        created_time: 记录创建时间，DateTime类型，UTC时间，自动设置

    **设计特点**：
        - 使用utf8mb4字符集，支持完整的Unicode字符
        - 时间字段使用`_time`后缀（符合项目规范）
        - 不使用物理外键约束（关系在应用层维护）
        - 不在ORM模型中定义索引和关系（在SQL DDL中定义）
        - task_id字段用于关联查询，但不使用ORM关系属性

    **与Pydantic模型的配合**：
        - 可以通过`TaskExecutionResponse.model_validate(execution)`自动转换
        - FastAPI会自动将SQLAlchemy模型转换为Pydantic响应模型
        - 确保字段类型与Pydantic模型匹配
    """

    __tablename__ = "task_executions"

    id = Column(
        Integer,
        primary_key=True,
        comment="执行记录ID，主键，自增",
    )

    task_id = Column(
        Integer,
        nullable=False,
        comment="关联的任务ID，外键关联tasks表",
    )

    status = Column(
        String(20),
        nullable=False,
        comment="执行状态：running-执行中, completed-成功, failed-失败",
    )

    result = Column(
        Text,
        nullable=True,
        comment="执行结果，JSON格式或文本格式，包含任务执行的输出内容",
    )

    error_message = Column(
        Text,
        nullable=True,
        comment="错误信息，当执行失败时记录详细的错误描述和堆栈信息",
    )

    execution_time = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        comment="任务执行时间，UTC时间",
    )

    duration_seconds = Column(
        Float,
        nullable=True,
        comment="任务执行耗时，单位：秒",
    )

    created_time = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="记录创建时间，UTC时间",
    )

    # 表选项
    __table_args__ = (
        # 字符集和排序规则设置
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_general_ci"},
    )

