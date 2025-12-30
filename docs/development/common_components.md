# 公共组件文档

本文档列出TimerOS项目中所有封装的公共组件。**所有开发人员必须使用这些组件，禁止重复开发相似功能。**

## 1. 日志组件

### 1.1 组件位置

- 文件路径：`app/utils/logger.py`
- 主要函数：`get_logger()`
- 配置函数：`setup_logging()`

### 1.2 功能说明

提供统一的日志记录功能，支持：
- 结构化日志（JSON格式）
- 多级别日志（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- 文件和控制台输出
- 上下文信息记录

### 1.3 使用方法

```python
from app.utils.logger import get_logger

# 获取日志记录器（推荐在模块顶部使用）
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("任务创建成功", extra={"task_id": 123})
logger.warning("警告信息", extra={"task_id": 123})
logger.error("错误信息", extra={"task_id": 123}, exc_info=True)
logger.critical("严重错误", extra={"task_id": 123}, exc_info=True)
```

### 1.4 注意事项

- **必须使用**：所有模块必须使用`get_logger(__name__)`获取日志记录器
- **禁止直接使用logging**：不要直接使用`logging.getLogger()`，必须使用`get_logger()`
- **使用extra参数**：记录上下文信息时使用`extra`参数，不要使用f-string格式化
- **异常记录**：记录异常时使用`exc_info=True`参数

### 1.5 错误示例

```python
# ❌ 错误：直接使用logging
import logging
logger = logging.getLogger(__name__)

# ❌ 错误：使用f-string格式化日志
logger.info(f"任务 {task_id} 创建成功")

# ✅ 正确：使用公共组件
from app.utils.logger import get_logger
logger = get_logger(__name__)
logger.info("任务创建成功", extra={"task_id": task_id})
```

## 2. 异常组件

### 2.1 组件位置

- 文件路径：`app/utils/exceptions.py`
- 基类：`TimerOSException`
- 具体异常：
  - `TaskParseError`: 任务解析错误
  - `TaskExecutionError`: 任务执行错误
  - `AIServiceError`: AI服务错误
  - `SchedulerError`: 任务调度错误
  - `DatabaseError`: 数据库操作错误

### 2.2 功能说明

提供项目特定的异常类型，用于更精确的错误处理和错误信息传递。

### 2.3 使用方法

```python
from app.utils.exceptions import (
    TimerOSException,
    TaskParseError,
    TaskExecutionError,
    AIServiceError,
    SchedulerError,
    DatabaseError
)

# 抛出异常
if not description:
    raise TaskParseError("任务描述不能为空")

# 捕获异常
try:
    result = parse_task(description)
except TaskParseError as e:
    logger.error(f"解析失败: {e}", exc_info=True)
    raise
```

### 2.4 注意事项

- **必须使用**：所有自定义异常必须继承自`TimerOSException`或其子类
- **禁止使用通用异常**：不要直接使用`Exception`或`ValueError`，使用项目特定的异常类型
- **异常链**：使用`raise ... from e`保持异常链
- **添加异常**：如需新的异常类型，在`exceptions.py`中添加，不要在其他地方定义

### 2.5 错误示例

```python
# ❌ 错误：直接使用通用异常
raise Exception("任务解析失败")
raise ValueError("任务描述不能为空")

# ✅ 正确：使用项目特定异常
from app.utils.exceptions import TaskParseError
raise TaskParseError("任务描述不能为空")
```

## 3. AI服务提供商基类

### 3.1 组件位置

- 文件路径：`app/ai_providers/base.py`
- 基类：`BaseAIProvider`

### 3.2 功能说明

定义AI服务提供商的统一接口，所有AI服务提供商必须实现此接口。

### 3.3 使用方法

```python
from app.ai_providers.base import BaseAIProvider

# 实现AI提供商
class MyAIProvider(BaseAIProvider):
    async def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs):
        # 实现逻辑
        pass
    
    async def generate_text(self, prompt, model=None, temperature=0.7, max_tokens=None, **kwargs):
        # 实现逻辑
        pass
```

### 3.4 注意事项

- **必须继承**：所有AI服务提供商必须继承自`BaseAIProvider`
- **实现所有方法**：必须实现`chat_completion()`和`generate_text()`方法
- **统一接口**：保持接口一致性，便于切换不同的AI服务
- **使用现有实现**：优先使用已有的`OpenAIProvider`、`AnthropicProvider`、`LocalProvider`

### 3.5 错误示例

```python
# ❌ 错误：不继承基类
class MyAIProvider:
    async def call_ai(self, prompt):
        pass

# ✅ 正确：继承基类
from app.ai_providers.base import BaseAIProvider
class MyAIProvider(BaseAIProvider):
    async def chat_completion(self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs):
        pass
    async def generate_text(self, prompt, model=None, temperature=0.7, max_tokens=None, **kwargs):
        pass
```

## 4. 辅助函数组件

### 4.1 组件位置

- 文件路径：`app/utils/helpers.py`
- 主要函数：
  - `utc_now()`: 获取当前UTC时间
  - `format_datetime()`: 格式化datetime
  - `parse_datetime()`: 解析时间字符串
  - `safe_get()`: 安全获取字典值
  - `validate_required_fields()`: 验证必需字段

### 4.2 功能说明

提供通用的辅助函数，包括时间处理、数据转换、验证等功能。

### 4.3 使用方法

```python
from app.utils.helpers import (
    utc_now,
    format_datetime,
    parse_datetime,
    safe_get,
    validate_required_fields
)

# 获取当前UTC时间
now = utc_now()

# 格式化时间
formatted = format_datetime(now, "%Y-%m-%d %H:%M:%S")

# 解析时间字符串
dt = parse_datetime("2024-01-15 09:00:00")

# 安全获取字典值
value = safe_get(data, "key", default="default_value")

# 验证必需字段
validate_required_fields(data, ["field1", "field2"])
```

### 4.4 注意事项

- **优先使用**：时间处理、数据验证等操作优先使用这些辅助函数
- **不要重复实现**：不要重复实现类似的功能
- **扩展函数**：如需新的辅助函数，在`helpers.py`中添加

## 5. 数据库组件

### 5.1 组件位置

- 文件路径：`app/core/database.py`
- 主要组件：
  - `Base`: SQLAlchemy基类
  - `get_db()`: 数据库会话依赖注入函数
  - `init_db()`: 数据库初始化函数

### 5.2 功能说明

提供数据库连接和会话管理功能。

### 5.3 使用方法

```python
from app.core.database import Base, get_db, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

# 定义数据模型
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)

# 在FastAPI中使用依赖注入
@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(MyModel).all()

# 手动创建会话
db = SessionLocal()
try:
    # 使用数据库会话
    pass
finally:
    db.close()
```

### 5.4 注意事项

- **必须使用Base**：所有数据模型必须继承自`Base`
- **使用依赖注入**：在FastAPI路由中使用`Depends(get_db)`
- **正确关闭会话**：手动创建会话时必须正确关闭
- **不要直接创建引擎**：使用`get_db()`或`SessionLocal`，不要直接创建数据库引擎

## 6. 配置管理组件

### 6.1 组件位置

- 文件路径：`config/settings.py`
- 配置类：`Settings`
- 全局实例：`settings`

### 6.2 功能说明

提供统一的配置管理，从环境变量和`.env`文件加载配置。

### 6.3 使用方法

```python
from config.settings import settings

# 访问配置
db_host = settings.MYSQL_HOST
api_key = settings.OPENAI_API_KEY
debug = settings.DEBUG

# 访问MySQL URL
mysql_url = settings.mysql_url
```

### 6.4 注意事项

- **必须使用**：所有配置访问必须通过`settings`对象
- **不要硬编码**：不要硬编码配置值，使用`settings`
- **环境变量优先**：配置优先从环境变量读取
- **添加配置**：如需新配置，在`Settings`类中添加

### 6.5 错误示例

```python
# ❌ 错误：硬编码配置
db_host = "localhost"
api_key = "sk-xxx"

# ✅ 正确：使用配置组件
from config.settings import settings
db_host = settings.MYSQL_HOST
api_key = settings.OPENAI_API_KEY
```

## 7. 数据模型基类

### 7.1 组件位置

- 文件路径：`app/core/models.py`
- 基类：`Base`（从`app.core.database`导入）

### 7.2 功能说明

所有数据模型必须继承自`Base`，确保统一的表结构和行为。

### 7.3 使用方法

```python
from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    name = Column(String(255), nullable=False, comment="名称")
    created_time = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")
```

### 7.4 注意事项

- **必须继承Base**：所有数据模型必须继承自`Base`
- **时间字段命名**：使用`created_time`和`updated_time`，不是`created_at`和`updated_at`
- **添加注释**：所有字段必须添加`comment`说明
- **字符集设置**：在`__table_args__`中设置字符集为`utf8mb4_general_ci`

## 8. 工具组件

### 8.1 网络搜索工具

- 位置：`app/tools/web_search.py`
- 类：`WebSearchTool`
- 用途：网络搜索功能

```python
from app.tools.web_search import WebSearchTool

tool = WebSearchTool()
results = await tool.search("搜索关键词", num_results=10)
```

### 8.2 邮件客户端

- 位置：`app/tools/email_client.py`
- 类：`EmailClient`
- 用途：发送邮件通知

```python
from app.tools.email_client import EmailClient

client = EmailClient()
client.send_email(
    to_addresses=["user@example.com"],
    subject="主题",
    body="正文"
)
```

### 8.3 Notion客户端

- 位置：`app/tools/notion_client.py`
- 类：`NotionClient`
- 用途：Notion API集成

```python
from app.tools.notion_client import NotionClient

client = NotionClient()
page = await client.create_page(
    database_id="database-id",
    title="页面标题",
    content={...}
)
```

### 8.4 数据分析工具

- 位置：`app/tools/data_analyzer.py`
- 类：`DataAnalyzer`
- 用途：数据分析功能

```python
from app.tools.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
result = analyzer.analyze_data(data)
summary = analyzer.generate_summary(data)
```

## 9. 使用原则

### 9.1 必须使用原则

1. **禁止重复开发**：如果公共组件已提供功能，必须使用公共组件，禁止重复开发
2. **统一接口**：使用统一的接口和规范，保持代码一致性
3. **扩展优先**：如需新功能，优先考虑扩展现有组件，而不是创建新组件

### 9.2 添加新组件

**重要：开发新公共组件时，必须更新本文档！**

如需添加新的公共组件，必须遵循以下步骤：

1. **在相应的工具模块中添加**（如`app/utils/`、`app/tools/`）
2. **必须更新本文档**：在本文档中添加新组件的详细说明，包括：
   - 组件位置（文件路径）
   - 功能说明
   - 使用方法（含完整代码示例）
   - 注意事项
   - 错误示例对比（如适用）
3. **更新组件列表总结表**：在本文档第10节"组件列表总结"中添加新组件条目
4. **在代码审查时说明**：为什么需要新组件，以及是否考虑过扩展现有组件

**注意**：未在本文档中记录的组件不能被视为公共组件，其他开发人员可能不知道其存在，导致重复开发。

### 9.3 代码审查检查点

代码审查时必须检查：

- [ ] 是否使用了公共日志组件（`get_logger`）
- [ ] 是否使用了公共异常类型
- [ ] 是否使用了公共配置管理（`settings`）
- [ ] 是否使用了公共数据库组件（`Base`、`get_db`）
- [ ] 是否使用了公共辅助函数
- [ ] 是否避免了重复开发已有功能
- [ ] **如果开发了新公共组件，是否已更新本文档（common_components.md）**

## 10. 组件列表总结

| 组件名称 | 位置 | 用途 | 必须使用 |
|---------|------|------|---------|
| `get_logger()` | `app/utils/logger.py` | 日志记录 | ✅ |
| `TimerOSException`系列 | `app/utils/exceptions.py` | 异常处理 | ✅ |
| `BaseAIProvider` | `app/ai_providers/base.py` | AI服务接口 | ✅ |
| `helpers`函数 | `app/utils/helpers.py` | 辅助函数 | ✅ |
| `Base`、`get_db()` | `app/core/database.py` | 数据库操作 | ✅ |
| `settings` | `config/settings.py` | 配置管理 | ✅ |
| `WebSearchTool` | `app/tools/web_search.py` | 网络搜索 | ✅ |
| `EmailClient` | `app/tools/email_client.py` | 邮件发送 | ✅ |
| `NotionClient` | `app/tools/notion_client.py` | Notion集成 | ✅ |
| `DataAnalyzer` | `app/tools/data_analyzer.py` | 数据分析 | ✅ |

## 11. 更新日志

- 2024-01-15: 初始版本，列出所有公共组件

