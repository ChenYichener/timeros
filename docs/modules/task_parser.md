# 任务解析模块

## 1. 模块概述

### 1.1 模块职责

任务解析模块负责将用户输入的自然语言任务描述解析为结构化的任务对象。主要功能包括：

- 解析自然语言时间表达式（如"明天上午9点"、"每周一8点"）
- 识别任务类型（研究任务、分析任务、报告任务）
- 提取任务参数（时间范围、数量限制等）
- 生成cron表达式（周期性任务）

### 1.2 模块位置

- 文件路径：`app/core/task_parser.py`
- 类名：`TaskParser`

### 1.3 依赖关系

- `app.ai_providers.base.BaseAIProvider`: AI服务提供商接口
- `app.utils.exceptions.TaskParseError`: 自定义异常
- `app.utils.logger`: 日志工具

## 2. API文档

### 2.1 类/函数列表

- `TaskParser`: 任务解析器主类
  - `__init__(llm_provider)`: 初始化解析器
  - `parse(description)`: 解析任务描述（异步方法）

### 2.2 详细API说明

#### TaskParser

任务解析器类，负责解析自然语言任务描述。

**方法列表**:

- `async parse(description: str) -> Dict[str, Any]`: 解析任务描述（异步方法）
- `_preprocess_description(description: str) -> str`: 预处理描述文本
- `async _parse_with_llm(description: str) -> Dict[str, Any]`: 使用LLM解析（包含当前时间信息）
- `_validate_parse_result(result: Dict) -> Dict[str, Any]`: 验证解析结果

**示例**:

```python
from app.ai_providers.openai_provider import OpenAIProvider
from app.core.task_parser import TaskParser

# 创建解析器
ai_provider = OpenAIProvider()
parser = TaskParser(llm_provider=ai_provider)

# 解析任务描述
result = await parser.parse("明天上午9点研究AI新闻")
print(result)
# {
#     "schedule": "2024-01-15T09:00:00",
#     "task_type": "research_task",
#     "params": {"topic": "AI新闻"},
#     "recurring": False
# }
```

## 3. 设计说明

### 3.1 设计思路

采用完全依赖LLM的解析策略：

1. **预处理**：清理输入文本，移除多余空格和特殊字符
2. **LLM解析**：调用LLM进行深度解析，理解自然语言表达
   - Prompt中包含详细的当前时间信息（日期、星期、时分等）
   - 确保LLM能正确计算相对时间表达（如"明天"、"下周X"等）
3. **结果验证**：确保解析结果的完整性和正确性
4. **缓存机制**：缓存解析结果，避免重复解析相同描述

**设计优势**：
- **完全依赖LLM**：所有解析都通过LLM完成，不依赖规则匹配，能处理更复杂的自然语言表达
- **时间感知**：Prompt中包含当前时间信息，避免LLM因不知道当前时间而错误计算调度时间
- **灵活性强**：能理解各种自然语言时间表达，不受规则限制

### 3.2 关键流程

```
用户输入 → 预处理 → LLM解析（包含当前时间信息） → 结果验证 → 缓存 → 返回结果
```

### 3.3 数据流

1. **输入**：自然语言任务描述字符串
2. **预处理**：清理文本，移除多余空格和特殊字符
3. **LLM解析**：调用LLM解析，Prompt中包含：
   - 当前时间信息（日期、星期、时分等）
   - 任务描述
   - 输出格式要求
4. **验证**：检查解析结果的必要字段和格式
5. **输出**：结构化任务对象（包含schedule、task_type、params、recurring、cron_expression等）

### 3.4 Prompt设计

LLM解析时使用的Prompt包含以下关键信息：

1. **当前时间信息**（重要）：
   - 当前时间（完整日期时间）
   - 当前日期
   - 当前星期
   - 当前年份、月份、日期、小时、分钟
   - 时间计算说明（如"明天"指的是当前日期的下一天）

2. **任务描述**：用户输入的自然语言任务描述

3. **输出要求**：
   - schedule：执行时间（ISO格式）
   - task_type：任务类型
   - params：任务参数
   - recurring：是否周期性任务
   - cron_expression：cron表达式（如果是周期性任务）

通过提供详细的当前时间信息，确保LLM能正确理解相对时间表达，避免因不知道当前时间而计算错误。

## 4. 配置说明

### 4.1 环境变量

无需额外环境变量，使用传入的AI提供商配置。

### 4.2 配置文件

无需额外配置文件。

## 5. 使用示例

### 5.1 基本使用

```python
from app.ai_providers.openai_provider import OpenAIProvider
from app.core.task_parser import TaskParser

ai_provider = OpenAIProvider()
parser = TaskParser(llm_provider=ai_provider)

# 解析一次性任务
result = await parser.parse("明天上午9点研究AI新闻")

# 解析周期性任务
result = await parser.parse("每周一上午8点分析竞争对手")
```

### 5.2 高级用法

```python
# 使用不同的AI提供商
from app.ai_providers.anthropic_provider import AnthropicProvider

ai_provider = AnthropicProvider()
parser = TaskParser(llm_provider=ai_provider)
result = await parser.parse("每月1号分析网站流量")
```

## 6. 常见问题

### Q: 解析失败怎么办？

A: 检查任务描述是否包含明确的时间信息。如果仍然失败，查看日志了解详细错误信息。

### Q: 支持哪些时间表达式？

A: 支持所有自然语言时间表达，包括但不限于：
- 相对时间："明天"、"后天"、"下周X"、"下个月X号"
- 绝对时间："2024年1月15日上午9点"
- 周期性："每周一"、"每月1号"、"每天上午8点"
- 复杂表达："下个工作日"、"每季度第一天"等

所有解析都通过LLM完成，能理解各种自然语言表达。

### Q: LLM如何知道当前时间？

A: 在每次解析时，系统会在Prompt中提供详细的当前时间信息，包括：
- 当前日期和时间
- 当前星期
- 当前年份、月份、日期、小时、分钟

这样LLM就能根据当前时间正确计算相对时间表达（如"明天"、"下周X"等）。

### Q: 解析结果可以缓存吗？

A: 是的，解析器内部有缓存机制，相同描述的解析结果会被缓存。

## 7. 更新日志

- 2024-12-30: 重构为完全依赖LLM解析，移除所有规则匹配逻辑；在Prompt中添加当前时间信息，确保LLM能正确计算调度时间
- 2024-01-15: 初始版本，支持基本的时间解析和任务类型识别

