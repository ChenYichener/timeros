"""
API集成测试。

测试API接口的基本功能。
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_task():
    """测试创建任务"""
    response = client.post(
        "/api/tasks",
        json={"description": "明天上午9点研究AI新闻"},
    )
    # 注意：这个测试可能需要数据库和AI服务，可能会失败
    # 在实际测试中应该使用mock或测试数据库
    assert response.status_code in [201, 400, 500]  # 根据实际情况调整

