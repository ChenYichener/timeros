"""
Pytest配置和fixtures模块。

定义测试中使用的fixtures，包括数据库会话、测试客户端、模拟LLM等。
这些fixtures可以在所有测试文件中使用。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, AsyncMock

from app.core.database import Base, get_db
from app.main import app

# 创建测试数据库引擎（使用内存数据库或测试数据库）
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    创建测试数据库会话。

    每个测试函数都会获得一个独立的数据库会话，测试结束后自动回滚。
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    创建测试客户端。

    用于测试API接口，自动注入测试数据库会话。
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_chat_model():
    """
    创建模拟的LangChain Chat模型。

    用于测试，避免实际调用AI服务。
    """
    from app.core.task_parser import ParsedTask

    mock = MagicMock()

    # 模拟with_structured_output方法
    structured_mock = MagicMock()
    structured_mock.ainvoke = AsyncMock(return_value=ParsedTask(
        schedule="2024-01-15T09:00:00",
        task_type="research_task",
        params={"topic": "测试主题"},
        recurring=False,
        cron_expression=None,
    ))
    mock.with_structured_output.return_value = structured_mock

    # 模拟bind_tools方法
    bound_mock = MagicMock()
    bound_mock.ainvoke = AsyncMock(return_value=MagicMock(
        content="任务执行完成",
        tool_calls=[],
    ))
    mock.bind_tools.return_value = bound_mock

    return mock


@pytest.fixture
def mock_task_parser(mock_chat_model):
    """
    创建模拟的任务解析器。

    使用模拟的Chat模型，避免实际调用AI服务。
    """
    from app.core.task_parser import TaskParser
    return TaskParser(llm=mock_chat_model)


@pytest.fixture
def mock_task_executor(mock_chat_model):
    """
    创建模拟的任务执行器。

    使用模拟的Chat模型，避免实际调用AI服务。
    """
    from app.core.executor import TaskExecutor
    return TaskExecutor(llm=mock_chat_model)


@pytest.fixture
def mock_task_agent(mock_chat_model):
    """
    创建模拟的任务Agent。

    用于测试Agent功能。
    """
    from app.agents.task_agent import TaskAgent
    from app.tools.langchain_tools import get_all_tools

    return TaskAgent(llm=mock_chat_model, tools=get_all_tools())
