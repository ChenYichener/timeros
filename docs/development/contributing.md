# 贡献指南

感谢您对TimerOS项目的关注！本文档将帮助您了解如何参与项目开发。

## 开发环境搭建

### 1. 克隆仓库

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

### 4. 配置环境变量

复制`.env.example`为`.env`并填写配置：

```bash
cp .env.example .env
```

### 5. 初始化数据库

```bash
python scripts/init_db.py
```

## 开发流程

### 1. 创建功能分支

```bash
git checkout -b feat/your-feature-name
```

### 2. 开发新功能

- 遵循编码标准（参考`docs/development/coding_standards.md`）
- 编写详细的文档字符串
- 添加类型提示
- 编写测试用例

### 3. 运行测试

```bash
pytest
```

### 4. 代码格式化

```bash
black .
isort .
ruff check .
mypy app/
```

### 5. 提交代码

使用Conventional Commits规范：

```bash
git commit -m "feat(module): 添加新功能"
```

### 6. 推送并创建Pull Request

```bash
git push origin feat/your-feature-name
```

## 代码审查

所有代码提交都需要经过审查：

1. 确保代码符合编码标准
2. 确保有相应的测试用例
3. 确保文档已更新
4. 确保所有检查通过

## 报告问题

如果发现bug或有功能建议，请创建Issue：

- 详细描述问题或建议
- 提供复现步骤（如适用）
- 说明期望的行为

## 联系方式

如有问题，请通过以下方式联系：

- 创建Issue
- 发送邮件

感谢您的贡献！

