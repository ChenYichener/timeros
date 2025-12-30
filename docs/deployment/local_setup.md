# 本地部署指南

本文档说明如何在本地环境搭建和运行TimerOS项目。

## 前置要求

- Python 3.11+
- MySQL 5.7+ 或 8.0+
- Git

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd timeros
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. 配置MySQL数据库

创建MySQL数据库：

```sql
CREATE DATABASE timeros CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 5. 配置环境变量

复制`.env.example`为`.env`：

```bash
cp .env.example .env
```

编辑`.env`文件，填写数据库配置：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=timeros

# AI服务配置（至少配置一个）
OPENAI_API_KEY=your_openai_api_key
# 或
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 6. 初始化数据库

```bash
python scripts/init_db.py
```

### 7. 启动应用

```bash
uvicorn app.main:app --reload
```

应用将在 `http://localhost:8000` 启动。

## 验证安装

### 1. 检查健康状态

```bash
curl http://localhost:8000/health
```

应该返回：`{"status": "healthy"}`

### 2. 查看API文档

访问 `http://localhost:8000/docs` 查看Swagger UI文档。

### 3. 测试创建任务

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{"description": "明天上午9点研究AI新闻"}'
```

## 常见问题

### 数据库连接失败

- 检查MySQL服务是否运行
- 检查`.env`中的数据库配置是否正确
- 检查数据库用户权限

### AI服务调用失败

- 检查API密钥是否正确配置
- 检查网络连接
- 查看日志文件了解详细错误

### 端口被占用

如果8000端口被占用，可以指定其他端口：

```bash
uvicorn app.main:app --reload --port 8001
```

## 开发工具

### 代码格式化

```bash
black .
isort .
```

### 代码检查

```bash
ruff check .
mypy app/
```

### 运行测试

```bash
pytest
```

## 下一步

- 阅读[API文档](../api/rest_api.md)了解如何使用API
- 阅读[开发规范](coding_standards.md)了解编码标准
- 查看[架构文档](../architecture.md)了解系统设计

