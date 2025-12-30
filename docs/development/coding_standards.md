# 编码标准文档

本文档详细说明了TimerOS项目的编码规范和开发标准。所有开发人员必须遵循这些规范。

**注意**：本文档是宏观规范总览，具体细节请参考：
- [公共组件文档](common_components.md) - 公共组件使用指南
- [贡献指南](contributing.md) - 开发流程和贡献指南
- [模块文档](../modules/) - 各模块详细文档

## 1. 项目结构规范

### 1.1 目录组织原则

- 按功能模块划分目录
- 每个模块独立目录，包含 `__init__.py`
- 配置文件统一放在 `config/` 目录
- 测试文件放在 `tests/` 目录，与源码结构对应
- 工具脚本放在 `scripts/` 目录
- 文档放在 `docs/` 目录

### 1.2 主要目录结构

```
timeros/
├── app/                  # 应用主目录
│   ├── api/             # API路由模块
│   ├── core/             # 核心业务逻辑
│   ├── services/         # 业务服务层
│   ├── ai_providers/     # AI提供商模块
│   ├── tools/            # 工具集成模块
│   └── utils/            # 工具函数
├── config/               # 配置文件目录
├── tests/                # 测试目录
├── scripts/               # 脚本目录
├── migrations/           # 数据库迁移（Alembic）
├── docs/                 # 文档目录
├── main.py               # 应用入口（通过uvicorn app.main:app启动）
├── pyproject.toml        # 项目配置
├── Makefile              # 常用命令封装
└── .pre-commit-config.yaml # Pre-commit配置
```

## 2. 代码风格

### 1.1 格式化工具

项目使用以下工具进行代码格式化：

- **black**: 代码格式化（行长度88字符）
- **isort**: 导入语句排序
- **ruff**: 代码检查（替代flake8）
- **mypy**: 静态类型检查

### 1.2 代码格式化命令

```bash
# 格式化代码
black .

# 整理import
isort .

# 检查代码
ruff check .

# 类型检查
mypy app/
```

### 1.3 行长度

- 最大行长度：88字符（black默认）
- 长行使用括号、反斜杠或字符串连接换行

### 1.4 导入顺序

1. 标准库导入
2. 第三方库导入
3. 本地应用导入
4. 每组之间空一行

```python
# 标准库
import os
from datetime import datetime

# 第三方库
from fastapi import FastAPI
from sqlalchemy.orm import Session

# 本地应用
from app.core.models import Task
from app.utils.logger import get_logger
```

## 2. 命名规范

### 2.1 文件命名
- Python文件：使用小写字母和下划线（snake_case）
- 示例：`task_parser.py`, `web_search.py`

### 2.2 类命名
- 使用大驼峰命名（PascalCase）
- 示例：`TaskParser`, `OpenAIProvider`

### 2.3 函数和变量命名
- 使用小写字母和下划线（snake_case）
- 示例：`parse_task()`, `task_status`

### 2.4 常量命名
- 使用全大写字母和下划线
- 示例：`MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`

### 2.5 私有成员命名
- 使用单下划线前缀表示内部使用：`_internal_cache`
- 使用双下划线前缀表示名称修饰（避免使用，除非必要）

### 2.6 数据库命名
- **表名**：使用复数形式，小写字母和下划线（如`tasks`, `task_executions`）
- **字段名**：使用小写字母和下划线（如`task_id`, `created_time`）
- **索引名**：`idx_表名_字段名`（如`idx_tasks_status`）

## 3. 注释规范

### 3.1 文档字符串

所有公共类、函数、方法必须有详细的文档字符串，使用Google风格：

```python
def parse_task_description(description: str) -> Dict[str, Any]:
    """
    解析任务描述，提取时间、任务类型和参数。
    
    Args:
        description: 用户输入的自然语言任务描述
        
    Returns:
        包含解析结果的字典
        
    Raises:
        TaskParseError: 当无法解析任务描述时
    """
    pass
```

### 3.2 行内注释

复杂逻辑必须添加行内注释，解释"为什么"而不是"做什么"：

```python
# 使用LLM解析时间表达式，因为自然语言时间表达复杂多样
# 规则解析无法覆盖所有情况
parsed_time = await llm_parse_time(description)
```

## 4. 类型提示

所有函数必须包含类型提示：

```python
from typing import Optional, List, Dict, Any

def create_task(
    description: str,
    schedule: Optional[str] = None,
    params: Optional[Dict[str, Any]] = None
) -> Task:
    pass
```

## 5. 异常处理

### 5.1 自定义异常

使用项目特定的异常类：

```python
from app.utils.exceptions import TaskParseError

try:
    result = parse_task(description)
except TaskParseError as e:
    logger.error(f"解析失败: {e}")
    raise
```

### 5.2 异常处理最佳实践

- 不要使用裸露的`except`
- 记录详细的错误信息
- 使用`exc_info=True`记录堆栈信息

## 6. 日志规范

### 6.1 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 确认程序按预期运行的信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 6.2 日志使用

```python
logger.info("任务创建成功", extra={"task_id": task.id})
logger.error("任务执行失败", extra={"task_id": task.id}, exc_info=True)
```

## 7. 数据模型规范

### 7.1 双层模型设计

系统采用**双层模型设计**，分别用于数据库映射和API层验证：

1. **SQLAlchemy ORM模型**（`app/core/models.py`）
   - 用于数据库表映射
   - 定义表结构和字段类型
   - 用于数据库操作（CRUD）

2. **Pydantic模型**（`app/core/schemas.py`）
   - 用于API层数据验证和序列化
   - **所有API接口必须使用Pydantic模型**
   - 自动进行类型验证和数据转换

### 7.2 Pydantic模型规范

#### 7.2.1 必须使用Pydantic模型

**所有API接口的输入输出都必须使用Pydantic模型进行验证和序列化。**

**请求模型**：
- 用于验证API请求参数（请求体、查询参数）
- 必须继承自`pydantic.BaseModel`
- 使用`Field()`提供字段描述和验证规则

**响应模型**：
- 用于序列化API响应数据
- 必须设置`from_attributes = True`以支持从SQLAlchemy模型转换
- 使用`response_model`参数在路由中指定

**示例**：
```python
from pydantic import BaseModel, Field

# 请求模型
class TaskCreate(BaseModel):
    description: str = Field(..., description="任务描述")

# 响应模型
class TaskResponse(BaseModel):
    id: int
    name: str
    status: str
    
    class Config:
        from_attributes = True  # 支持从SQLAlchemy模型转换

# API路由中使用
@router.post("", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    # task_data已通过Pydantic验证
    pass
```

#### 7.2.2 Pydantic模型命名规范

- **请求模型**：使用`Create`、`Update`后缀，如`TaskCreate`、`TaskUpdate`
- **响应模型**：使用`Response`后缀，如`TaskResponse`、`TaskExecutionResponse`
- **列表响应**：使用`ListResponse`后缀，如`TaskListResponse`
- **基础模型**：使用`Base`后缀，如`TaskBase`（用于继承）

#### 7.2.3 Pydantic模型字段规范

- 所有字段必须提供类型提示
- 使用`Field()`提供字段描述（`description`参数）
- 可选字段使用`Optional[Type] = None`或`Type | None = None`
- 必填字段使用`...`（Ellipsis）或直接定义类型

**示例**：
```python
class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    status: Optional[str] = Field(None, description="任务状态")
```

### 7.3 SQLAlchemy ORM模型规范

#### 7.3.1 字段命名

- 时间戳字段使用`_time`后缀：`created_time`, `updated_time`（不是`created_at`）
- 外键字段命名：`表名_id`，如`task_id`

#### 7.3.2 表设计

- 所有表必须有主键（`id`），使用自增整数类型
- 必须有`created_time`和`updated_time`字段
- 所有字段必须添加`comment`注释说明字段用途
- 字符集：`utf8mb4`，排序规则：`utf8mb4_general_ci`
- 存储引擎：`InnoDB`

#### 7.3.3 索引规范

- **禁止在ORM模型中定义索引**：索引应在SQL DDL中显式定义，而不是通过ORM模型。
- 为常用查询字段添加索引
- 索引命名：`idx_表名_字段名`
- 复合索引用于多字段查询

#### 7.3.4 外键规范

**禁止使用物理外键约束**

- **不使用数据库层面的外键约束（FOREIGN KEY）**
- 表之间的关联关系通过应用层代码维护
- 外键字段仍然需要添加索引以提高查询性能
- 数据完整性由应用层代码保证

**原因：**
- 提高数据库性能，避免外键检查带来的开销
- 简化数据库迁移和维护
- 提高灵活性，便于数据分片和扩展
- 避免级联删除等操作可能带来的意外影响

**示例：**
```sql
-- ✅ 正确：只添加索引，不使用物理外键
CREATE TABLE task_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL COMMENT '关联的任务ID',
    -- ... 其他字段
    INDEX idx_executions_task_id (task_id)  -- 添加索引提高查询性能
);

-- ❌ 错误：使用物理外键约束
CREATE TABLE task_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    CONSTRAINT fk_executions_task_id FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

#### 7.3.5 ORM关系规范

- **禁止在ORM模型中定义关系**：ORM模型（如`app/core/models.py`中的`Task`和`TaskExecution`）不应包含`relationship()`定义。
- **直接通过字段关联**：所有表之间的关联查询应通过外键字段（如`task_id`）直接进行，而不是通过ORM关系属性。
- **原因**：
  - **简化模型**：使ORM模型更简洁，只关注表结构。
  - **避免复杂性**：避免SQLAlchemy关系定义可能带来的复杂性，尤其是在不使用物理外键的情况下。
  - **明确性**：强制开发人员在需要关联查询时显式编写JOIN语句，提高SQL的透明度。

### 7.4 模型转换规范

#### 7.4.1 SQLAlchemy → Pydantic

使用Pydantic的`from_attributes = True`配置，自动从SQLAlchemy模型转换：

```python
# SQLAlchemy模型
task = db.query(Task).filter(Task.id == task_id).first()

# 自动转换为Pydantic模型
task_response = TaskResponse.model_validate(task)
# 或使用FastAPI自动转换（在response_model中指定）
```

#### 7.4.2 Pydantic → SQLAlchemy

手动创建SQLAlchemy模型实例：

```python
# Pydantic模型
task_create = TaskCreate(description="任务描述")

# 创建SQLAlchemy模型
task = Task(
    description=task_create.description,
    # ... 其他字段
)
```

## 8. 配置管理规范

### 8.1 环境变量

- 使用`.env`文件管理配置
- 敏感信息（API密钥、密码）必须使用环境变量
- 提供`.env.example`作为模板

### 8.2 配置访问

- **必须使用**`config.settings.settings`访问配置
- 禁止硬编码配置值
- 配置优先从环境变量读取

## 9. Git提交规范

使用Conventional Commits规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

类型：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

示例：
```
feat(scheduler): 添加周期性任务支持

支持每周、每月等周期性任务调度
- 实现cron表达式解析
- 添加任务重复执行逻辑
```

## 10. 测试规范

### 10.1 测试文件组织

- 测试文件与源码结构对应
- 使用`pytest`作为测试框架
- 测试函数命名：`test_功能描述`

### 10.2 测试要求

- 所有公共API必须有测试
- 测试覆盖率应达到80%以上
- 使用fixtures管理测试数据

## 11. 公共组件使用规范

### 10.1 必须使用公共组件

**所有开发人员必须使用项目中封装的公共组件，禁止重复开发相似功能。**

详细组件列表和使用方法请参考：[公共组件文档](common_components.md)

### 10.2 核心原则

1. **禁止重复开发**：如果公共组件已提供功能，必须使用公共组件
2. **统一接口**：使用统一的接口和规范，保持代码一致性
3. **扩展优先**：如需新功能，优先考虑扩展现有组件

### 10.3 必须使用的组件

- **日志组件**：必须使用`app.utils.logger.get_logger()`
- **异常组件**：必须使用`app.utils.exceptions`中的异常类型
- **配置管理**：必须使用`config.settings.settings`
- **数据库组件**：必须使用`app.core.database.Base`和`get_db()`
- **AI服务接口**：必须继承`app.ai_providers.base.BaseAIProvider`

### 10.4 代码审查检查

代码审查时必须检查是否使用了公共组件，避免重复开发。

## 12. 模块开发流程

### 12.1 开发前准备

在开发新模块前，必须：

1. **文档先行**：在`docs/modules/`目录下创建详细的模块说明文档
2. **API设计**：明确模块的接口和API
3. **实现开发**：按照文档进行代码实现
4. **文档更新**：开发完成后更新文档，确保文档与代码一致

### 12.2 模块文档要求

模块文档必须包含：
- 模块概述（职责、位置、依赖关系）
- API文档（所有公共类、函数、方法的详细说明）
- 设计说明（设计思路、关键流程、数据流）
- 配置说明（环境变量、配置文件）
- 使用示例（基本使用、高级用法）
- 常见问题

详细要求参考：[开发规范 - 模块开发流程](#12-模块开发流程)

## 13. 公共组件开发规范

### 13.1 开发新公共组件

如需添加新的公共组件，必须：

1. 在相应的工具模块中添加（如`app/utils/`、`app/tools/`）
2. **必须更新公共组件文档**：在`docs/development/common_components.md`中添加详细说明
3. 更新组件列表总结表
4. 在代码审查时说明为什么需要新组件

详细要求参考：[公共组件文档](common_components.md)

## 14. 代码审查清单

提交代码前必须检查以下所有项：

### 14.1 代码质量

- [ ] 代码通过black格式化
- [ ] 代码通过ruff检查（无错误）
- [ ] 代码通过mypy类型检查（无错误）
- [ ] 所有函数有类型提示
- [ ] 所有公共API有详细的文档字符串（Google风格）
- [ ] 复杂逻辑有行内注释（解释"为什么"）

### 14.2 命名规范

- [ ] 文件、类、函数、变量命名符合规范
- [ ] 数据库表名、字段名、索引名符合规范
- [ ] 常量使用全大写命名

### 14.3 公共组件使用

- [ ] **使用了公共日志组件**（`get_logger`）
- [ ] **使用了公共异常类型**（`TimerOSException`系列）
- [ ] **使用了公共配置管理**（`settings`）
- [ ] **使用了公共数据库组件**（`Base`、`get_db`）
- [ ] **没有重复开发已有功能**

### 14.4 数据模型使用

- [ ] **所有API接口使用了Pydantic模型进行验证**（请求和响应）
- [ ] Pydantic模型命名符合规范（Create、Update、Response后缀）
- [ ] Pydantic模型字段提供了类型提示和描述
- [ ] 响应模型设置了`from_attributes = True`
- [ ] SQLAlchemy ORM模型没有定义关系和索引

### 14.5 文档和测试

- [ ] 有相应的测试用例（覆盖率≥80%）
- [ ] 更新了相关文档
- [ ] **如果开发了新模块，已创建模块文档**（`docs/modules/`）
- [ ] **如果开发了新公共组件，已更新[公共组件文档](common_components.md)**

### 14.6 Git提交

- [ ] 提交信息符合Conventional Commits规范
- [ ] 提交信息清晰描述变更内容

## 15. 快速参考

### 15.1 相关文档

- [公共组件文档](common_components.md) - 所有公共组件的详细说明和使用方法
- [贡献指南](contributing.md) - 开发环境搭建和开发流程
- [模块文档](../modules/) - 各模块的详细API文档

### 15.2 常用命令

```bash
# 代码格式化
black . && isort .

# 代码检查
ruff check . && mypy app/

# 运行测试
pytest

# 查看测试覆盖率
pytest --cov=app --cov-report=html
```

