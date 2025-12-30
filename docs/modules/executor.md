# 任务执行模块

## 1. 模块概述

### 1.1 模块职责

任务执行模块负责执行各种类型的任务，包括：

- 研究任务：搜索信息、生成摘要
- 分析任务：分析数据、生成报告
- 报告任务：生成报告并发布

### 1.2 模块位置

- 文件路径：`app/core/executor.py`
- 类名：`TaskExecutor`

### 1.3 依赖关系

- `app.ai_providers.base.BaseAIProvider`: AI服务提供商
- `app.tools.web_search.WebSearchTool`: 网络搜索工具
- `app.tools.email_client.EmailClient`: 邮件客户端
- `app.tools.notion_client.NotionClient`: Notion客户端
- `app.tools.data_analyzer.DataAnalyzer`: 数据分析工具
- `app.core.models`: 数据模型

## 2. API文档

### 2.1 类/函数列表

- `TaskExecutor`: 任务执行器类
  - `execute_task()`: 执行任务（异步方法）
  - `_execute_research_task()`: 执行研究任务
  - `_execute_analysis_task()`: 执行分析任务
  - `_execute_report_task()`: 执行报告任务

### 2.2 详细API说明

#### TaskExecutor

任务执行器类，负责执行各种类型的任务。

**方法列表**:

- `async execute_task(task_id, db) -> Dict[str, Any]`: 执行任务
- `async _execute_research_task(task, db) -> Dict[str, Any]`: 执行研究任务
- `async _execute_analysis_task(task, db) -> Dict[str, Any]`: 执行分析任务
- `async _execute_report_task(task, db) -> Dict[str, Any]`: 执行报告任务

**示例**:

```python
from app.core.executor import TaskExecutor
from app.ai_providers.openai_provider import OpenAIProvider

ai_provider = OpenAIProvider()
executor = TaskExecutor(ai_provider=ai_provider)

# 执行任务
result = await executor.execute_task(task_id=1, db=db)
print(result)
```

## 3. 设计说明

### 3.1 设计思路

采用策略模式，根据任务类型调用相应的处理器：

- **研究任务**：搜索 → AI分析 → 生成摘要 → 发送通知
- **分析任务**：收集数据 → 分析 → AI生成报告
- **报告任务**：收集数据 → AI生成报告 → 发布到Notion

### 3.2 关键流程

```
任务执行开始 → 更新状态为running → 根据任务类型执行 → 保存结果 → 更新状态
```

### 3.3 数据流

1. 从数据库加载任务信息
2. 根据任务类型执行相应逻辑
3. 保存执行结果到数据库
4. 更新任务状态

## 4. 配置说明

### 4.1 环境变量

依赖AI服务和工具服务的配置（见各工具模块文档）。

### 4.2 配置文件

无需额外配置文件。

## 5. 使用示例

### 5.1 基本使用

```python
from app.core.executor import TaskExecutor
from app.ai_providers.openai_provider import OpenAIProvider
from app.core.database import SessionLocal

ai_provider = OpenAIProvider()
executor = TaskExecutor(ai_provider=ai_provider)

db = SessionLocal()
try:
    result = await executor.execute_task(task_id=1, db=db)
    print(f"执行成功: {result['status']}")
finally:
    db.close()
```

### 5.2 自定义工具

```python
from app.tools.web_search import WebSearchTool
from app.tools.email_client import EmailClient

web_search = WebSearchTool()
email_client = EmailClient()

executor = TaskExecutor(
    ai_provider=ai_provider,
    web_search=web_search,
    email_client=email_client
)
```

## 6. 常见问题

### Q: 任务执行失败怎么办？

A: 执行失败会记录错误信息到数据库，任务状态会更新为failed。查看执行记录了解详细错误。

### Q: 如何添加新的任务类型？

A: 在`TaskExecutor`类中添加新的`_execute_xxx_task`方法，并在`execute_task`方法中添加相应的分支。

### Q: 任务执行是同步还是异步？

A: 任务执行是异步的，使用`async/await`语法，不会阻塞其他任务。

## 7. 更新日志

- 2024-01-15: 初始版本，支持研究任务、分析任务、报告任务

