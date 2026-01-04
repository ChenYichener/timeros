# AI服务提供商模块

> **注意**: 此模块已被LangChain替代。请使用 `app.llm` 和 `app.agents` 模块。

## 1. 模块概述

### 1.1 新架构说明

从 v2.0 开始，项目已迁移到 LangChain 1.0 生态系统。新的模块结构如下：

- **LLM工厂**: `app/llm/factory.py` - 创建LangChain Chat模型
- **Agent模块**: `app/agents/task_agent.py` - LangGraph自主决策Agent
- **工具模块**: `app/tools/langchain_tools.py` - LangChain Tool格式的工具

### 1.2 依赖关系

新依赖：
- `langchain-core`: LangChain核心组件
- `langchain-openai`: OpenAI集成
- `langchain-anthropic`: Anthropic集成
- `langchain-community`: 社区集成（Ollama等）
- `langgraph`: Agent编排框架

## 2. 新API文档

### 2.1 LLM工厂 (`app/llm/factory.py`)

#### get_chat_model()

获取LangChain Chat模型实例。

```python
from app.llm.factory import get_chat_model

# 使用默认配置
llm = get_chat_model()

# 指定提供商和模型
llm = get_chat_model(
    provider="openai",
    model="gpt-4",
    temperature=0.7
)
```

**参数**:
- `provider`: AI提供商 ("openai", "anthropic", "local")
- `model`: 模型名称
- `temperature`: 温度参数 (0-1)

**返回**: `BaseChatModel` 实例

### 2.2 任务Agent (`app/agents/task_agent.py`)

#### TaskAgent类

使用LangGraph实现的自主决策Agent。

```python
from app.agents.task_agent import TaskAgent
from app.llm.factory import get_chat_model
from app.tools.langchain_tools import get_all_tools

llm = get_chat_model()
agent = TaskAgent(llm=llm, tools=get_all_tools())

# 执行任务
result = await agent.execute(
    task_description="搜索最新的AI新闻并生成摘要",
    task_params={"topic": "AI新闻", "time_range": "24小时"}
)
```

**方法**:
- `execute(task_description, task_params)`: 执行任务
- `stream_execute(task_description, task_params)`: 流式执行任务

### 2.3 LangChain工具 (`app/tools/langchain_tools.py`)

可用工具列表：
- `web_search`: 网络搜索
- `search_news`: 新闻搜索
- `send_email`: 发送邮件
- `send_task_result_email`: 发送任务结果邮件
- `create_notion_page`: 创建Notion页面
- `update_notion_page`: 更新Notion页面
- `analyze_data`: 数据分析
- `generate_data_summary`: 生成数据摘要

```python
from app.tools.langchain_tools import get_all_tools, get_research_tools

# 获取所有工具
all_tools = get_all_tools()

# 获取研究任务相关工具
research_tools = get_research_tools()
```

## 3. 设计说明

### 3.1 架构图

```
┌──────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                    │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│                    TaskParser                             │
│         (使用LangChain结构化输出解析任务)                  │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│                    TaskExecutor                           │
│              (调用LangGraph Agent)                        │
└────────────────────────────┬─────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────┐
│                    LangGraph Agent                        │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│   │  LLM Node   │◄──►│  Tool Node  │◄──►│   Tools     │  │
│   └─────────────┘    └─────────────┘    └─────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 3.2 工作流程

1. **任务解析**: 使用 `TaskParser` 解析自然语言描述
2. **Agent调用**: `TaskExecutor` 创建并调用 `TaskAgent`
3. **自主决策**: Agent根据任务描述自主选择工具
4. **工具执行**: 调用相应的LangChain工具
5. **结果返回**: Agent汇总结果并返回

## 4. 配置说明

### 4.1 环境变量

```bash
# AI提供商选择
AI_PROVIDER=openai  # 可选: openai, anthropic, local

# OpenAI配置
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，用于自定义端点

# Anthropic配置
ANTHROPIC_API_KEY=your-api-key
```

## 5. 迁移指南

### 5.1 从旧版本迁移

**旧代码**:
```python
from app.ai_providers.openai_provider import OpenAIProvider

provider = OpenAIProvider()
result = await provider.generate_text("请分析...")
```

**新代码**:
```python
from app.llm.factory import get_chat_model
from langchain_core.messages import HumanMessage

llm = get_chat_model()
result = await llm.ainvoke([HumanMessage(content="请分析...")])
```

### 5.2 使用Agent执行任务

**旧方式**: 手动编排工具调用

**新方式**: 让Agent自主决策
```python
from app.agents.task_agent import TaskAgent
from app.llm.factory import get_chat_model

agent = TaskAgent(llm=get_chat_model())
result = await agent.execute("搜索AI新闻并生成摘要")
```

## 6. 已废弃的API

以下API已废弃，将在未来版本中移除：

- `app.ai_providers.base.BaseAIProvider`
- `app.ai_providers.openai_provider.OpenAIProvider`
- `app.ai_providers.anthropic_provider.AnthropicProvider`
- `app.ai_providers.local_provider.LocalProvider`
- `app.api.dependencies.get_ai_provider()`

## 7. 更新日志

- 2026-01-04: 迁移到LangChain 1.0，添加LangGraph Agent支持
- 2024-01-15: 初始版本，支持OpenAI、Anthropic和本地模型
