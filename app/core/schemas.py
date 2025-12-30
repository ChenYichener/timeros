"""
Pydantic模式定义模块。

定义API请求和响应的数据模式，用于数据验证和序列化。
所有API接口的输入输出都使用这些模式进行验证。
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """
    任务基础模式。

    包含任务的通用字段，用于创建和更新任务。
    """

    name: Optional[str] = Field(None, description="任务名称")
    description: str = Field(..., description="任务描述，自然语言")
    task_type: Optional[str] = Field(None, description="任务类型")
    schedule: Optional[datetime] = Field(None, description="执行时间")
    cron_expression: Optional[str] = Field(None, description="Cron表达式")
    is_recurring: bool = Field(False, description="是否为周期性任务")
    params: Optional[Dict[str, Any]] = Field(None, description="任务参数")


class TaskCreate(TaskBase):
    """
    创建任务的请求模式。

    用于POST /tasks接口，接收用户输入的自然语言任务描述。
    """

    description: str = Field(..., description="任务描述，自然语言格式")


class TaskUpdate(BaseModel):
    """
    更新任务的请求模式。

    用于PUT /tasks/{id}接口，所有字段都是可选的。
    """

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class TaskResponse(TaskBase):
    """
    任务响应模式。

    用于返回任务信息，包含所有任务字段和ID、时间戳等。
    """

    id: int
    status: str
    created_time: datetime
    updated_time: datetime
    deleted_time: Optional[datetime] = None

    class Config:
        """Pydantic配置"""

        from_attributes = True


class TaskExecutionResponse(BaseModel):
    """
    任务执行记录响应模式。

    用于返回任务执行历史记录。
    """

    id: int
    task_id: int
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: datetime
    duration_seconds: Optional[float] = None
    created_time: datetime

    class Config:
        """Pydantic配置"""

        from_attributes = True


class TaskListResponse(BaseModel):
    """
    任务列表响应模式。

    用于返回任务列表，包含分页信息。
    """

    tasks: list[TaskResponse]
    total: int
    page: int
    page_size: int

