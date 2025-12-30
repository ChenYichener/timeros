"""
任务执行引擎模块。

该模块负责执行各种类型的任务，包括研究任务、分析任务、报告任务等。
根据任务类型调用相应的处理器，处理任务执行过程中的错误，并保存执行结果。
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.ai_providers.base import BaseAIProvider
from app.core.database import get_db
from app.core.models import Task, TaskExecution
from app.tools.data_analyzer import DataAnalyzer
from app.tools.email_client import EmailClient
from app.tools.notion_client import NotionClient
from app.tools.web_search import WebSearchTool
from app.utils.exceptions import TaskExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TaskExecutor:
    """
    任务执行引擎类。

    负责执行各种类型的任务，包括：
    - 研究任务：搜索信息、生成摘要
    - 分析任务：分析数据、生成报告
    - 报告任务：生成报告并发布

    支持错误处理、重试机制、结果保存等功能。
    """

    def __init__(
        self,
        ai_provider: BaseAIProvider,
        web_search: Optional[WebSearchTool] = None,
        email_client: Optional[EmailClient] = None,
        notion_client: Optional[NotionClient] = None,
        data_analyzer: Optional[DataAnalyzer] = None,
    ):
        """
        初始化任务执行引擎。

        Args:
            ai_provider: AI服务提供商，用于生成文本、分析等
            web_search: 网络搜索工具，用于研究任务
            email_client: 邮件客户端，用于发送通知
            notion_client: Notion客户端，用于发布报告
            data_analyzer: 数据分析工具，用于分析任务
        """
        self.ai_provider = ai_provider
        self.web_search = web_search or WebSearchTool()
        self.email_client = email_client or EmailClient()
        self.notion_client = notion_client or NotionClient()
        self.data_analyzer = data_analyzer or DataAnalyzer()

    async def execute_task(self, task_id: int, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        执行任务。

        根据任务类型调用相应的处理器，处理执行过程中的错误，
        并保存执行结果到数据库。

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

            # 记录开始时间
            start_time = time.time()

            # 根据任务类型执行相应的处理逻辑
            if task.task_type == "research_task":
                result = await self._execute_research_task(task, db)
            elif task.task_type == "analysis_task":
                result = await self._execute_analysis_task(task, db)
            elif task.task_type == "report_task":
                result = await self._execute_report_task(task, db)
            else:
                raise TaskExecutionError(f"未知的任务类型: {task.task_type}")

            # 计算执行耗时
            duration = time.time() - start_time

            # 更新执行记录
            execution.status = "completed"
            execution.result = json.dumps(result, ensure_ascii=False)
            execution.duration_seconds = duration
            db.commit()

            # 更新任务状态
            if task.is_recurring:
                # 周期性任务保持pending状态，等待下次执行
                task.status = "pending"
            else:
                # 一次性任务标记为completed
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

        except Exception as e:
            # 处理执行错误
            error_message = str(e)
            logger.error(
                f"任务执行失败: task_id={task_id}, error={error_message}",
                extra={"task_id": task_id, "error": error_message},
                exc_info=True,
            )

            # 更新执行记录
            if "execution" in locals():
                execution.status = "failed"
                execution.error_message = error_message
                execution.duration_seconds = time.time() - start_time
                db.commit()

            # 更新任务状态
            if "task" in locals():
                task.status = "failed"
                db.commit()

            raise TaskExecutionError(f"任务执行失败: {error_message}") from e

    async def _execute_research_task(
        self, task: Task, db: Session
    ) -> Dict[str, Any]:
        """
        执行研究任务。

        研究任务通常包括：
        1. 使用网络搜索工具搜索相关信息
        2. 使用AI分析搜索结果
        3. 生成摘要
        4. 发送结果（如需要）

        Args:
            task: 任务对象
            db: 数据库会话

        Returns:
            执行结果字典
        """
        logger.debug(f"执行研究任务: task_id={task.id}")

        # 获取任务参数
        params = task.params or {}
        topic = params.get("topic", "AI新闻")
        time_range = params.get("time_range", "24小时")

        # 步骤1: 搜索相关信息
        search_query = f"{topic} {time_range}"
        search_results = await self.web_search.search_news(
            query=search_query, time_range="24h", num_results=10
        )

        if not search_results:
            return {"message": "未找到相关信息", "results": []}

        # 步骤2: 使用AI生成摘要
        # 构建prompt
        results_text = "\n".join(
            [
                f"{i+1}. {r['title']}\n   {r['snippet']}\n   {r['link']}"
                for i, r in enumerate(search_results[:5])
            ]
        )

        prompt = f"""
请分析以下搜索结果，生成一份简洁的摘要报告。

搜索结果：
{results_text}

请生成一份包含以下内容的摘要：
1. 主要发现（3-5个要点）
2. 关键信息总结
3. 相关链接

请用中文回答，保持简洁明了。
"""

        summary = await self.ai_provider.generate_text(
            prompt=prompt, temperature=0.7, max_tokens=1000
        )

        # 步骤3: 构建结果
        result = {
            "topic": topic,
            "time_range": time_range,
            "search_results_count": len(search_results),
            "summary": summary,
            "sources": [
                {"title": r["title"], "link": r["link"]} for r in search_results[:5]
            ],
        }

        # 步骤4: 如果任务参数中指定了发送邮件，则发送
        if params.get("send_email"):
            email_addresses = params.get("email_addresses", [])
            if email_addresses:
                try:
                    self.email_client.send_task_result(
                        to_addresses=email_addresses,
                        task_name=task.name,
                        result=summary,
                        is_success=True,
                    )
                except Exception as e:
                    logger.warning(f"发送邮件失败: {str(e)}")

        return result

    async def _execute_analysis_task(
        self, task: Task, db: Session
    ) -> Dict[str, Any]:
        """
        执行分析任务。

        分析任务通常包括：
        1. 收集数据
        2. 使用数据分析工具分析
        3. 使用AI生成分析报告
        4. 发布结果（如需要）

        Args:
            task: 任务对象
            db: 数据库会话

        Returns:
            执行结果字典
        """
        logger.debug(f"执行分析任务: task_id={task.id}")

        # 获取任务参数
        params = task.params or {}
        target = params.get("target", "数据")
        count = params.get("count", 5)

        # 步骤1: 收集数据（这里简化处理，实际应该从数据源获取）
        # 例如：从数据库、API等获取数据
        data = []  # 这里应该是实际的数据

        # 步骤2: 分析数据
        if data:
            analysis_result = self.data_analyzer.analyze_data(data)
            summary = self.data_analyzer.generate_summary(data)
        else:
            analysis_result = {}
            summary = "暂无数据可分析"

        # 步骤3: 使用AI生成分析报告
        prompt = f"""
请基于以下分析结果，生成一份详细的分析报告。

分析目标: {target}
分析数量: {count}

分析结果:
{json.dumps(analysis_result, ensure_ascii=False, indent=2)}

数据摘要:
{summary}

请生成一份包含以下内容的分析报告：
1. 执行摘要
2. 关键发现
3. 详细分析
4. 建议和结论

请用中文回答，保持专业和详细。
"""

        report = await self.ai_provider.generate_text(
            prompt=prompt, temperature=0.7, max_tokens=2000
        )

        # 步骤4: 构建结果
        result = {
            "target": target,
            "count": count,
            "analysis": analysis_result,
            "summary": summary,
            "report": report,
        }

        return result

    async def _execute_report_task(self, task: Task, db: Session) -> Dict[str, Any]:
        """
        执行报告任务。

        报告任务通常包括：
        1. 收集数据
        2. 使用AI生成报告
        3. 发布到Notion或其他平台

        Args:
            task: 任务对象
            db: 数据库会话

        Returns:
            执行结果字典
        """
        logger.debug(f"执行报告任务: task_id={task.id}")

        # 获取任务参数
        params = task.params or {}
        report_type = params.get("report_type", "流量分析")

        # 步骤1: 收集数据（这里简化处理）
        # 实际应该从数据源获取，如网站流量数据
        data = {}

        # 步骤2: 使用AI生成报告
        prompt = f"""
请基于以下数据，生成一份详细的{report_type}报告。

数据类型: {report_type}
数据内容: {json.dumps(data, ensure_ascii=False, indent=2) if data else "暂无数据"}

请生成一份包含以下内容的报告：
1. 执行摘要
2. 关键指标
3. 趋势分析
4. 结论和建议

请用中文回答，保持专业和详细。
"""

        report = await self.ai_provider.generate_text(
            prompt=prompt, temperature=0.7, max_tokens=2000
        )

        # 步骤3: 发布到Notion（如果配置了）
        notion_page_id = None
        if params.get("publish_to_notion"):
            database_id = params.get("notion_database_id")
            if database_id:
                try:
                    notion_result = await self.notion_client.create_page(
                        database_id=database_id,
                        title=f"{report_type}报告 - {datetime.utcnow().strftime('%Y-%m-%d')}",
                        content={
                            "报告内容": {
                                "rich_text": [
                                    {
                                        "text": {
                                            "content": report[:2000],  # Notion限制
                                        }
                                    }
                                ]
                            }
                        },
                    )
                    notion_page_id = notion_result.get("id")
                except Exception as e:
                    logger.warning(f"发布到Notion失败: {str(e)}")

        # 步骤4: 构建结果
        result = {
            "report_type": report_type,
            "report": report,
            "notion_page_id": notion_page_id,
        }

        return result

