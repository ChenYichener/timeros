# TimerOS - AI定时任务系统

一个基于AI的智能定时任务系统，支持通过自然语言创建和管理定时任务。

## 功能特性

- 🤖 **AI驱动**: 使用大语言模型解析自然语言任务描述
- ⏰ **灵活调度**: 支持一次性任务和周期性任务（每天、每周、每月）
- 🔌 **多AI支持**: 支持OpenAI、Anthropic和本地模型
- 🛠️ **丰富工具**: 集成网络搜索、Notion、邮件等工具
- 📊 **任务追踪**: 完整的任务执行历史和状态管理

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

### 3. 初始化数据库

有三种方式初始化数据库，选择其中一种：

**方式1：使用SQL DDL文件（快速初始化）**

```bash
mysql -u root -p < scripts/schema.sql
```

**方式2：使用Python脚本初始化（开发环境）**

```bash
python scripts/init_db.py
```

**方式3：使用Alembic迁移（推荐，生产环境）**

```bash
# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 方式1：直接启动
uvicorn app.main:app --reload

# 方式2：使用Makefile（推荐）
make run
```

## 使用示例

### 创建一次性任务

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "明天上午9点运行此任务：研究过去24小时内的热门AI新闻并向我发送摘要"
  }'
```

### 创建周期性任务

```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "每周一上午8点，研究我们的前5名竞争对手，并向我发送产品更新摘要"
  }'
```

## 项目结构

```
timeros/
├── app/                  # 应用主目录
│   ├── api/             # API路由模块
│   ├── core/             # 核心业务逻辑
│   ├── services/         # 业务服务层
│   ├── ai_providers/     # AI提供商模块
│   ├── tools/            # 工具集成模块
│   └── utils/            # 工具函数
├── config/               # 配置文件
├── tests/                # 测试文件
├── scripts/              # 脚本文件
│   ├── schema.sql        # SQL DDL文件（数据库表结构）
│   ├── init.sql          # 数据库初始化脚本（Docker用）
│   └── init_db.py        # Python数据库初始化脚本
├── migrations/           # 数据库迁移（Alembic）
├── docs/                 # 文档目录
├── .env.example          # 环境变量配置模板
├── main.py               # 应用入口（通过uvicorn app.main:app启动）
├── pyproject.toml        # 项目配置和工具配置
├── requirements.txt      # 生产依赖
├── requirements-dev.txt   # 开发依赖
├── Dockerfile            # Docker镜像配置
├── docker-compose.yml    # Docker Compose配置
├── Makefile              # 常用命令封装
└── .pre-commit-config.yaml # Pre-commit hooks配置
```

## 开发工具

### 使用Makefile

项目提供了Makefile，封装了常用命令：

```bash
make help          # 查看所有可用命令
make install-dev    # 安装开发依赖
make format         # 格式化代码
make lint           # 代码检查
make type-check     # 类型检查
make test           # 运行测试
make test-cov       # 测试覆盖率
make run            # 启动开发服务器
```

### Pre-commit Hooks

安装pre-commit hooks，在提交代码前自动检查：

```bash
pre-commit install
```

### Docker支持

使用Docker快速启动开发环境：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

## 开发规范

请参考 `docs/development/coding_standards.md` 了解详细的开发规范。

## 许可证

MIT License

