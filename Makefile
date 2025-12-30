.PHONY: help install install-dev format lint type-check test test-cov clean run init-db migrate upgrade-db docker-build docker-up docker-down

help: ## 显示帮助信息
	@echo "TimerOS 项目 Makefile"
	@echo ""
	@echo "可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装生产依赖
	pip install -r requirements.txt

install-dev: ## 安装开发依赖
	pip install -r requirements-dev.txt
	pre-commit install

format: ## 格式化代码
	black .
	isort .

lint: ## 代码检查
	ruff check .

type-check: ## 类型检查
	mypy app/

check: format lint type-check ## 运行所有检查（格式化、lint、类型检查）

test: ## 运行测试
	pytest

test-cov: ## 运行测试并生成覆盖率报告
	pytest --cov=app --cov-report=html --cov-report=term-missing

clean: ## 清理临时文件
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name ".ruff_cache" -exec rm -r {} +
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

run: ## 启动开发服务器
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

init-db: ## 初始化数据库
	python scripts/init_db.py

migrate: ## 创建数据库迁移
	alembic revision --autogenerate -m "$(msg)"

upgrade-db: ## 升级数据库
	alembic upgrade head

downgrade-db: ## 降级数据库
	alembic downgrade -1

docker-build: ## 构建Docker镜像
	docker-compose build

docker-up: ## 启动Docker容器
	docker-compose up -d

docker-down: ## 停止Docker容器
	docker-compose down

docker-logs: ## 查看Docker日志
	docker-compose logs -f

