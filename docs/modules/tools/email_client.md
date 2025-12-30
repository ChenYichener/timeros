# 邮件客户端模块

## 1. 模块概述

### 1.1 模块职责

邮件客户端提供邮件发送功能，用于任务执行结果的通知。

### 1.2 模块位置

- 文件路径：`app/tools/email_client.py`
- 类名：`EmailClient`

## 2. API文档

### 2.1 类/函数列表

- `EmailClient`: 邮件客户端类
  - `send_email()`: 发送邮件
  - `send_task_result()`: 发送任务执行结果

### 2.2 详细API说明

#### EmailClient

邮件客户端类。

**方法列表**:

- `send_email(to_addresses, subject, body, is_html) -> bool`: 发送邮件
- `send_task_result(to_addresses, task_name, result, is_success) -> bool`: 发送任务结果

**示例**:

```python
from app.tools.email_client import EmailClient

client = EmailClient()
client.send_email(
    to_addresses=["user@example.com"],
    subject="任务完成",
    body="任务执行成功"
)
```

## 3. 配置说明

### 3.1 环境变量

- `SMTP_HOST`: SMTP服务器地址
- `SMTP_PORT`: SMTP端口
- `SMTP_USER`: SMTP用户名
- `SMTP_PASSWORD`: SMTP密码

## 4. 使用示例

```python
from app.tools.email_client import EmailClient

client = EmailClient()

# 发送任务结果
client.send_task_result(
    to_addresses=["user@example.com"],
    task_name="研究AI新闻",
    result="找到了10条相关新闻...",
    is_success=True
)
```

