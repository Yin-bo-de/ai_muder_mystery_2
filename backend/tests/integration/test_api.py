"""API接口集成测试"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestAPI:
    """API接口测试"""

    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["project"] == "AI Murder Mystery"
        assert "version" in data

    def test_docs_accessible(self):
        """测试API文档可访问"""
        response = client.get("/docs")
        assert response.status_code == 200

    class TestUserAPI:
        """用户相关接口测试"""

        def test_get_user_info(self):
            """测试获取用户信息"""
            response = client.get("/api/v1/user/info?user_id=test_user")
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == "test_user"
            assert data["nickname"] == "侦探"
            assert "solved_cases" in data
            assert "rank" in data

        def test_get_user_history(self):
            """测试获取用户历史"""
            response = client.get("/api/v1/user/history?user_id=test_user")
            assert response.status_code == 200
            data = response.json()
            assert "total" in data
            assert "records" in data
            assert isinstance(data["records"], list)

        def test_get_user_statistics(self):
            """测试获取用户统计信息"""
            response = client.get("/api/v1/user/statistics?user_id=test_user")
            assert response.status_code == 200
            data = response.json()
            assert "total_cases" in data
            assert "solved_cases" in data
            assert "success_rate" in data
            assert "total_play_time_minutes" in data

    class TestGameAPI:
        """游戏相关接口测试"""

        def test_get_nonexistent_session_status(self):
            """测试获取不存在的会话状态"""
            response = client.get("/api/v1/game/nonexistent_session/status")
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001
            assert "会话不存在" in data["message"]

        def test_submit_investigation_nonexistent_session(self):
            """测试向不存在的会话提交勘查"""
            response = client.post(
                "/api/v1/game/nonexistent_session/investigate",
                json={"scene": "客厅", "item": "桌子"}
            )
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

        def test_decrypt_clue_nonexistent_session(self):
            """测试向不存在的会话提交解密"""
            response = client.post(
                "/api/v1/game/nonexistent_session/decrypt",
                json={"clue_id": "c1", "password": "123456"}
            )
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

        def test_accuse_nonexistent_session(self):
            """测试向不存在的会话提交指认"""
            response = client.post(
                "/api/v1/game/nonexistent_session/accuse",
                json={
                    "suspect_id": "s1",
                    "motive": "test motive",
                    "modus_operandi": "test modus",
                    "evidence": ["c1"]
                }
            )
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

        def test_get_clues_nonexistent_session(self):
            """测试获取不存在会话的线索"""
            response = client.get("/api/v1/game/nonexistent_session/clues")
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

    class TestAgentAPI:
        """AI交互相关接口测试"""

        def test_send_message_nonexistent_session(self):
            """测试向不存在的会话发送消息"""
            response = client.post(
                "/api/v1/agent/nonexistent_session/send",
                json={"message": "你好"}
            )
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

        def test_switch_mode_nonexistent_session(self):
            """测试向不存在的会话切换模式"""
            response = client.post(
                "/api/v1/agent/nonexistent_session/mode",
                json={"mode": "single", "suspect_id": "s1"}
            )
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

        def test_execute_command_nonexistent_session(self):
            """测试向不存在的会话执行指令"""
            response = client.post(
                "/api/v1/agent/nonexistent_session/command",
                json={"command": "keep_quiet"}
            )
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

        def test_get_history_nonexistent_session(self):
            """测试获取不存在会话的对话历史"""
            response = client.get("/api/v1/agent/nonexistent_session/history")
            assert response.status_code == 404
            data = response.json()
            assert data["code"] == 10001

    def test_invalid_endpoint(self):
        """测试访问不存在的端点"""
        response = client.get("/api/v1/nonexistent_endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        """测试不允许的HTTP方法"""
        response = client.put("/api/v1/user/info")
        assert response.status_code == 405
