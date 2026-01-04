"""
LangGraph任务执行Agent模块。

该模块实现基于LangGraph的自主决策Agent，用于执行各种类型的任务。
Agent可以自主决定调用哪些工具来完成任务。
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from app.agents.states import TaskExecutionState
from app.tools.langchain_tools import get_all_tools
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Agent系统提示词
TASK_AGENT_SYSTEM_PROMPT = """你是一个智能任务执行助手。你的职责是根据用户的任务描述，自主决定使用哪些工具来完成任务。

当前时间: {current_time}

你可以使用以下工具：
- web_search: 搜索网络获取信息
- search_news: 搜索最新新闻
- send_email: 发送电子邮件  
- send_task_result_email: 发送任务结果邮件
- create_notion_page: 在Notion中创建页面
- update_notion_page: 更新Notion页面
- analyze_data: 分析数据
- generate_data_summary: 生成数据摘要

执行任务时请遵循以下原则：
1. 仔细理解任务需求，确定需要使用哪些工具
2. 按照合理的顺序调用工具
3. 根据任务要求，可能需要多次调用工具
4. 如果任务要求发送结果（如邮件、Notion），确保在完成主要工作后执行
5. 最终提供清晰的任务完成总结

请使用中文与用户交流。"""


class TaskAgent:
    """
    LangGraph任务执行Agent类。

    封装LangGraph图的创建和执行，提供简洁的接口。
    """

    def __init__(
        self,
        llm: BaseChatModel,
        tools: Optional[List[BaseTool]] = None,
    ):
        """
        初始化任务执行Agent。

        Args:
            llm: LangChain Chat模型实例
            tools: 可用的工具列表，如果为None则使用所有工具
        """
        self.llm = llm
        self.tools = tools or get_all_tools()

        # 绑定工具到LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # 创建编译后的图
        self.graph = self._build_graph()

        logger.info(f"TaskAgent初始化完成，可用工具数量: {len(self.tools)}")

    def _build_graph(self) -> CompiledStateGraph:
        """
        构建LangGraph状态图。

        Returns:
            编译后的状态图
        """
        # 创建状态图
        graph = StateGraph(TaskExecutionState)

        # 添加节点
        graph.add_node("agent", self._agent_node)
        graph.add_node("tools", ToolNode(self.tools))

        # 添加边
        graph.add_edge(START, "agent")
        graph.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        graph.add_edge("tools", "agent")

        return graph.compile()

    def _get_system_message(self) -> SystemMessage:
        """
        获取系统消息。

        Returns:
            包含当前时间的系统消息
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return SystemMessage(
            content=TASK_AGENT_SYSTEM_PROMPT.format(current_time=current_time)
        )

    async def _agent_node(self, state: TaskExecutionState) -> Dict[str, Any]:
        """
        Agent节点：调用LLM决定下一步行动。

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        messages = list(state["messages"])

        # 确保系统消息在最前面
        if not messages or not isinstance(messages[0], SystemMessage):
            messages.insert(0, self._get_system_message())

        # 调用LLM
        response = await self.llm_with_tools.ainvoke(messages)

        return {"messages": [response]}

    def _should_continue(
        self, state: TaskExecutionState
    ) -> Literal["continue", "end"]:
        """
        决定是否继续执行。

        检查最后一条消息是否包含工具调用。

        Args:
            state: 当前状态

        Returns:
            "continue" 继续调用工具，"end" 结束执行
        """
        messages = state["messages"]
        last_message = messages[-1]

        # 检查是否有工具调用
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "continue"

        return "end"

    async def execute(
        self,
        task_description: str,
        task_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        执行任务。

        Args:
            task_description: 任务描述
            task_params: 任务参数

        Returns:
            执行结果字典
        """
        logger.info(f"开始执行任务: {task_description[:100]}...")

        # 构建初始消息
        user_message = task_description
        if task_params:
            user_message += f"\n\n任务参数: {task_params}"

        initial_state: TaskExecutionState = {
            "messages": [HumanMessage(content=user_message)],
            "task_description": task_description,
            "task_params": task_params,
            "final_result": None,
        }

        try:
            # 执行图
            final_state = await self.graph.ainvoke(initial_state)

            # 提取最终结果
            messages = final_state["messages"]
            last_message = messages[-1]

            result = {
                "success": True,
                "final_response": (
                    last_message.content
                    if isinstance(last_message, AIMessage)
                    else str(last_message)
                ),
                "message_count": len(messages),
            }

            logger.info(f"任务执行完成，消息数量: {len(messages)}")
            return result

        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "error": error_msg,
            }

    async def stream_execute(
        self,
        task_description: str,
        task_params: Optional[Dict[str, Any]] = None,
    ):
        """
        流式执行任务。

        Args:
            task_description: 任务描述
            task_params: 任务参数

        Yields:
            执行过程中的状态更新
        """
        logger.info(f"开始流式执行任务: {task_description[:100]}...")

        user_message = task_description
        if task_params:
            user_message += f"\n\n任务参数: {task_params}"

        initial_state: TaskExecutionState = {
            "messages": [HumanMessage(content=user_message)],
            "task_description": task_description,
            "task_params": task_params,
            "final_result": None,
        }

        async for event in self.graph.astream(initial_state):
            yield event


def create_task_agent(
    llm: BaseChatModel,
    tools: Optional[List[BaseTool]] = None,
) -> TaskAgent:
    """
    创建任务执行Agent。

    Args:
        llm: LangChain Chat模型实例
        tools: 可用的工具列表

    Returns:
        TaskAgent实例
    """
    return TaskAgent(llm=llm, tools=tools)
