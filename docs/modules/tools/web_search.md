# 网络搜索工具模块

## 1. 模块概述

### 1.1 模块职责

网络搜索工具提供网络搜索功能，用于研究任务中搜索信息。

### 1.2 模块位置

- 文件路径：`app/tools/web_search.py`
- 类名：`WebSearchTool`

### 1.3 依赖关系

- `serpapi`: SerpAPI服务（可选）
- `httpx`: HTTP客户端

## 2. API文档

### 2.1 类/函数列表

- `WebSearchTool`: 网络搜索工具类
  - `search()`: 执行搜索
  - `search_news()`: 搜索新闻

### 2.2 详细API说明

#### WebSearchTool

网络搜索工具类。

**方法列表**:

- `async search(query, num_results, language, **kwargs) -> List[Dict]`: 执行搜索
- `async search_news(query, time_range, num_results) -> List[Dict]`: 搜索新闻

**示例**:

```python
from app.tools.web_search import WebSearchTool

tool = WebSearchTool()
results = await tool.search("AI新闻", num_results=10)
```

## 3. 配置说明

### 3.1 环境变量

- `SERPAPI_KEY`: SerpAPI密钥（可选）

## 4. 使用示例

```python
from app.tools.web_search import WebSearchTool

tool = WebSearchTool()

# 普通搜索
results = await tool.search("Python教程", num_results=10)

# 新闻搜索
news = await tool.search_news("AI新闻", time_range="24h", num_results=10)
```

