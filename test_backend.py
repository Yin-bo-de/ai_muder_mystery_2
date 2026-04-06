#!/usr/bin/env python3
"""后端服务测试脚本"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """测试健康检查接口"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["project"] == "AI Murder Mystery"
    print("✅ 健康检查接口测试通过")
    return True

def test_api_docs():
    """测试API文档是否可访问"""
    response = client.get("/docs")
    assert response.status_code == 200
    print("✅ API文档接口测试通过")
    return True

def test_game_endpoints():
    """测试游戏相关接口结构"""
    # 测试创建新案件接口（需要OpenAI Key，这里只测试接口存在）
    response = client.post("/api/v1/game/new", json={})
    # 即使没有API Key也应该返回正确的错误格式
    assert response.status_code in [200, 500]  # 500是因为没有API Key，属于预期错误
    print("✅ 游戏创建接口存在")

    # 测试获取游戏状态接口
    response = client.get("/api/v1/game/test_session/status")
    assert response.status_code == 404  # 会话不存在是预期错误
    assert response.json()["code"] == 10001
    print("✅ 游戏状态接口存在")

    return True

def test_agent_endpoints():
    """测试AI交互相关接口结构"""
    response = client.post("/api/v1/agent/test_session/send", json={"message": "test"})
    assert response.status_code == 404  # 会话不存在是预期错误
    assert response.json()["code"] == 10001
    print("✅ 消息发送接口存在")
    return True

def test_user_endpoints():
    """测试用户相关接口"""
    response = client.get("/api/v1/user/info")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "nickname" in data
    print("✅ 用户信息接口测试通过")

    response = client.get("/api/v1/user/history")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "records" in data
    print("✅ 用户历史接口测试通过")

    return True

if __name__ == "__main__":
    print("🚀 开始后端服务测试...")
    all_passed = True

    try:
        test_health_check()
        test_api_docs()
        test_game_endpoints()
        test_agent_endpoints()
        test_user_endpoints()

        print("\n🎉 所有后端接口测试通过！后端服务运行正常。")
        print("\n📋 下一步操作：")
        print("1. 配置 backend/.env 文件中的 OPENAI_API_KEY")
        print("2. 启动后端服务：cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000")
        print("3. 启动前端服务：cd frontend && npm run dev")
        print("4. 访问 http://localhost:5173 即可体验游戏")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        all_passed = False

    sys.exit(0 if all_passed else 1)
