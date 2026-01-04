"""
Agent状态定义模块。

该模块定义LangGraph Agent使用的状态类型。
"""

from typing import Annotated, Any, Dict, List, Literal, Optional, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Agent状态类型。

    包含Agent执行过程中需要维护的所有状态信息。
    """

    # 消息历史，使用add_messages reducer自动合并消息
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # 任务相关信息
    task_id: Optional[int]
    task_type: Optional[str]
    task_params: Optional[Dict[str, Any]]

    # 执行状态
    execution_status: Literal["pending", "running", "completed", "failed"]

    # 执行结果
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]


class TaskExecutionState(TypedDict):
    """
    任务执行状态类型。

    用于简化的任务执行流程。
    """

    # 消息历史
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # 任务描述
    task_description: str

    # 任务参数
    task_params: Optional[Dict[str, Any]]

    # 最终结果
    final_result: Optional[str]
