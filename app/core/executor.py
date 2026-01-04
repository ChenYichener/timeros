"""
任务执行引擎模块。

该模块负责执行各种类型的任务，使用LangGraph Agent自主决策使用哪些工具。
Agent会根据任务描述自动选择合适的工具来完成任务。
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import BaseTool
from sqlalchemy.orm import Session

from app.agents.task_agent import TaskAgent
from app.core.database import get_db
from app.core.models import Task, TaskExecution
from app.tools.langchain_tools import (
    get_all_tools,
    get_analysis_tools,
    get_report_tools,
    get_research_tools,
)
from app.utils.exceptions import TaskExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskExecutor:
    """
    任务执行引擎类。

    使用LangGraph Agent自主决策执行任务，Agent会根据任务描述
    自动选择合适的工具来完成任务。

    支持的任务类型：
    - 研究任务：搜索信息、生成摘要
    - 分析任务：分析数据、生成报告
    - 报告任务：生成报告并发布
    """

    def __init__(
        self,
        llm: BaseChatModel,
        tools: Optional[List[BaseTool]] = None,
    ):
        """
        初始化任务执行引擎。

        Args:
            llm: LangChain Chat模型实例
            tools: 可用的工具列表，如果为None则使用所有工具
        """
        self.llm = llm
        self.tools = tools or get_all_tools()

        # 创建Agent实例
        self.agent = TaskAgent(llm=llm, tools=self.tools)

        logger.info(f"TaskExecutor初始化完成，可用工具数量: {len(self.tools)}")

    def _get_tools_for_task_type(self, task_type: str) -> List[BaseTool]:
        """
        根据任务类型获取相关工具。

        Args:
            task_type: 任务类型

        Returns:
            工具列表
        """
        if task_type == "research_task":
            return get_research_tools()
        elif task_type == "analysis_task":
            return get_analysis_tools()
        elif task_type == "report_task":
            return get_report_tools()
        else:
            return get_all_tools()

    def _build_task_prompt(self, task: Task) -> str:
        """
        构建任务执行的提示词。

        根据任务类型和参数构建详细的执行指令。

        Args:
            task: 任务对象

        Returns:
            任务执行提示词
        """
        params = task.params or {}
        task_type = task.task_type

        # 基础提示
        prompt_parts = [
            f"请执行以下任务：",
            f"",
            f"任务名称: {task.name}",
            f"任务描述: {task.description}",
            f"任务类型: {task_type}",
        ]

        # 添加任务参数
        if params:
            prompt_parts.append(f"任务参数: {json.dumps(params, ensure_ascii=False)}")

        # 根据任务类型添加具体指令
        if task_type == "research_task":
            topic = params.get("topic", "相关主题")
            time_range = params.get("time_range", "24小时")
            prompt_parts.extend([
                "",
                "执行要求：",
                f"1. 搜索关于 '{topic}' 的最新信息（时间范围：{time_range}）",
                "2. 分析搜索结果，提取关键信息",
                "3. 生成一份简洁的摘要报告，包含主要发现和关键信息",
            ])
            if params.get("send_email"):
                email_addresses = params.get("email_addresses", [])
                if email_addresses:
                    prompt_parts.append(
                        f"4. 将结果通过邮件发送到: {', '.join(email_addresses)}"
                    )

        elif task_type == "analysis_task":
            target = params.get("target", "数据")
            count = params.get("count", 5)
            prompt_parts.extend([
                "",
                "执行要求：",
                f"1. 分析目标: {target}",
                f"2. 分析数量: {count}",
                "3. 生成详细的分析报告，包含关键发现和建议",
            ])

        elif task_type == "report_task":
            report_type = params.get("report_type", "报告")
            prompt_parts.extend([
                "",
                "执行要求：",
                f"1. 生成{report_type}",
                "2. 报告应包含：执行摘要、关键指标、趋势分析、结论和建议",
            ])
            if params.get("publish_to_notion"):
                database_id = params.get("notion_database_id", "")
                if database_id:
                    prompt_parts.append(f"3. 将报告发布到Notion数据库: {database_id}")

        prompt_parts.extend([
            "",
            "请使用可用的工具完成上述任务，并提供详细的执行结果。",
        ])

        return "\n".join(prompt_parts)

    async def execute_task(
        self, task_id: int, db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        执行任务。

        使用LangGraph Agent自主决策执行任务，并保存执行结果到数据库。

        Args:
            task_id: 任务ID
            db: 数据库会话，如果为None则创建新会话

        Returns:
            执行结果字典，包含status、result等字段

        Raises:
            TaskExecutionError: 当任务执行失败时
        """
        # 获取数据库会话
        if db is None:
            db_gen = get_db()
            db = next(db_gen)

        execution = None
        task = None
        start_time = time.time()

        try:
            # 查询任务
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                raise TaskExecutionError(f"任务不存在: task_id={task_id}")

            logger.info(
                f"开始执行任务: task_id={task_id}, task_type={task.task_type}",
                extra={"task_id": task_id, "task_type": task.task_type},
            )

            # 更新任务状态为running
            task.status = "running"
            db.commit()

            # 创建执行记录
            execution = TaskExecution(
                task_id=task_id,
                status="running",
                execution_time=datetime.utcnow(),
            )
            db.add(execution)
            db.commit()

            # 构建任务提示词
            task_prompt = self._build_task_prompt(task)

            # 根据任务类型选择工具（可选，也可以使用所有工具让Agent自己选择）
            task_tools = self._get_tools_for_task_type(task.task_type)

            # 创建针对此任务的Agent（使用特定工具集）
            task_agent = TaskAgent(llm=self.llm, tools=task_tools)

            # 执行任务
            agent_result = await task_agent.execute(
                task_description=task_prompt,
                task_params=task.params,
            )

            # 计算执行耗时
            duration = time.time() - start_time

            # 处理执行结果
            if agent_result.get("success"):
                # 构建结果
                result = {
                    "task_type": task.task_type,
                    "agent_response": agent_result.get("final_response", ""),
                    "message_count": agent_result.get("message_count", 0),
                }

                # 更新执行记录
                execution.status = "completed"
                execution.result = json.dumps(result, ensure_ascii=False)
                execution.duration_seconds = duration
                db.commit()

                # 更新任务状态
                if task.is_recurring:
                    task.status = "pending"
                else:
                    task.status = "completed"
                db.commit()

                logger.info(
                    f"任务执行成功: task_id={task_id}, duration={duration:.2f}s",
                    extra={"task_id": task_id, "duration": duration},
                )

                return {
                    "status": "completed",
                    "result": result,
                    "duration_seconds": duration,
                }

            else:
                # 执行失败
                error_message = agent_result.get("error", "未知错误")
                raise TaskExecutionError(f"Agent执行失败: {error_message}")

        except Exception as e:
            # 处理执行错误
            error_message = str(e)
            duration = time.time() - start_time

            logger.error(
                f"任务执行失败: task_id={task_id}, error={error_message}",
                extra={"task_id": task_id, "error": error_message},
                exc_info=True,
            )

            # 更新执行记录
            if execution is not None:
                execution.status = "failed"
                execution.error_message = error_message
                execution.duration_seconds = duration
                db.commit()

            # 更新任务状态
            if task is not None:
                task.status = "failed"
                db.commit()

            raise TaskExecutionError(f"任务执行失败: {error_message}") from e

    async def execute_task_with_streaming(
        self, task_id: int, db: Optional[Session] = None
    ):
        """
        流式执行任务。

        支持实时返回执行过程中的状态更新。

        Args:
            task_id: 任务ID
            db: 数据库会话

        Yields:
            执行过程中的状态更新
        """
        if db is None:
            db_gen = get_db()
            db = next(db_gen)

        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                yield {"error": f"任务不存在: task_id={task_id}"}
                return

            # 构建任务提示词
            task_prompt = self._build_task_prompt(task)

            # 使用流式执行
            async for event in self.agent.stream_execute(
                task_description=task_prompt,
                task_params=task.params,
            ):
                yield event

        except Exception as e:
            yield {"error": str(e)}
