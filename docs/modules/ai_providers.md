# AI服务提供商模块

## 1. 模块概述

### 1.1 模块职责

AI服务提供商模块提供统一的AI服务接口，支持多种AI服务提供商：

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- 本地模型 (Ollama等)

### 1.2 模块位置

- 基础类：`app/ai_providers/base.py`
- OpenAI实现：`app/ai_providers/openai_provider.py`
- Anthropic实现：`app/ai_providers/anthropic_provider.py`
- 本地模型实现：`app/ai_providers/local_provider.py`

### 1.3 依赖关系

- `openai`: OpenAI官方SDK
- `anthropic`: Anthropic官方SDK
- `httpx`: HTTP客户端（本地模型使用）

## 2. API文档

### 2.1 类/函数列表

- `BaseAIProvider`: AI提供商基类
- `OpenAIProvider`: OpenAI提供商实现
- `AnthropicProvider`: Anthropic提供商实现
- `LocalProvider`: 本地模型提供商实现

### 2.2 详细API说明

#### BaseAIProvider

AI服务提供商基类，定义统一接口。

**方法列表**:

- `async chat_completion(messages, model, temperature, max_tokens, **kwargs) -> str`: 对话补全
- `async generate_text(prompt, model, temperature, max_tokens, **kwargs) -> str`: 生成文本

#### OpenAIProvider

OpenAI服务提供商实现。

**示例**:

```python
from app.ai_providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(api_key="your-api-key")
result = await provider.generate_text("请分析以下内容...")
```

#### AnthropicProvider

Anthropic服务提供商实现。

**示例**:

```python
from app.ai_providers.anthropic_provider import AnthropicProvider

provider = AnthropicProvider(api_key="your-api-key")
result = await provider.generate_text("请分析以下内容...")
```

#### LocalProvider

本地模型服务提供商实现。

**示例**:

```python
from app.ai_providers.local_provider import LocalProvider

provider = LocalProvider(base_url="http://localhost:11434", default_model="llama2")
result = await provider.generate_text("请分析以下内容...")
```

## 3. 设计说明

### 3.1 设计思路

采用策略模式和适配器模式：

- 定义统一的`BaseAIProvider`接口
- 各提供商实现统一接口
- 可以方便地切换不同的AI服务

### 3.2 关键流程

```
调用请求 → 统一接口 → 具体提供商实现 → API调用 → 返回结果
```

## 4. 配置说明

### 4.1 环境变量

- `OPENAI_API_KEY`: OpenAI API密钥
- `ANTHROPIC_API_KEY`: Anthropic API密钥

### 4.2 配置文件

无需额外配置文件，通过环境变量配置。

## 5. 使用示例

### 5.1 使用OpenAI

```python
from app.ai_providers.openai_provider import OpenAIProvider

provider = OpenAIProvider()
result = await provider.chat_completion([
    {"role": "user", "content": "请分析以下内容..."}
])
```

### 5.2 使用Anthropic

```python
from app.ai_providers.anthropic_provider import AnthropicProvider

provider = AnthropicProvider()
result = await provider.generate_text("请分析以下内容...")
```

### 5.3 使用本地模型

```python
from app.ai_providers.local_provider import LocalProvider

provider = LocalProvider(base_url="http://localhost:11434")
result = await provider.generate_text("请分析以下内容...")
```

## 6. 常见问题

### Q: 如何切换AI服务提供商？

A: 修改`app/api/dependencies.py`中的`get_ai_provider()`函数，或通过环境变量控制。

### Q: 支持哪些模型？

A: OpenAI支持GPT-4、GPT-3.5等；Anthropic支持Claude 3等；本地模型取决于Ollama安装的模型。

### Q: API调用失败怎么办？

A: 检查API密钥是否正确，网络连接是否正常，查看日志了解详细错误。

## 7. 更新日志

- 2024-01-15: 初始版本，支持OpenAI、Anthropic和本地模型

