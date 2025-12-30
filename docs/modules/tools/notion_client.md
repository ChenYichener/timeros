# Notion客户端模块

## 1. 模块概述

### 1.1 模块职责

Notion客户端提供Notion API集成功能，用于将任务执行结果发布到Notion数据库。

### 1.2 模块位置

- 文件路径：`app/tools/notion_client.py`
- 类名：`NotionClient`

## 2. API文档

### 2.1 类/函数列表

- `NotionClient`: Notion客户端类
  - `create_page()`: 创建页面
  - `update_page()`: 更新页面

### 2.2 详细API说明

#### NotionClient

Notion客户端类。

**方法列表**:

- `async create_page(database_id, title, content, **kwargs) -> Dict`: 创建页面
- `async update_page(page_id, properties, **kwargs) -> Dict`: 更新页面

**示例**:

```python
from app.tools.notion_client import NotionClient

client = NotionClient()
result = await client.create_page(
    database_id="your-database-id",
    title="报告标题",
    content={"报告内容": {"rich_text": [{"text": {"content": "报告正文"}}]}}
)
```

## 3. 配置说明

### 3.1 环境变量

- `NOTION_API_KEY`: Notion API密钥

## 4. 使用示例

```python
from app.tools.notion_client import NotionClient

client = NotionClient()

# 创建报告页面
page = await client.create_page(
    database_id="your-database-id",
    title="网站流量分析报告",
    content={
        "报告内容": {
            "rich_text": [{"text": {"content": "报告正文内容"}}]
        }
    }
)
```

