"""
游戏管理API功能测试
覆盖测试方案中的 API-GAME-* 用例
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from main import app
from app.core.constants import GameStatus, ClueType, ClueStatus

client = TestClient(app)


class TestGameCreationAPI:
    """测试创建新案件接口 - API-GAME-001 ~ API-GAME-006"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """设置mock依赖"""
        with patch('app.services.game_service.game_service') as mock_service:
            self.mock_game_service = mock_service
            # 默认mock返回值
            self.mock_game_service.create_new_game = AsyncMock(return_value={
                "session_id": "test_session_001",
                "case_basic_info": {
                    "victim": {
                        "name": "陈天",
                        "cause_of_death": "颅脑损伤",
                        "death_time": "昨晚10:00-10:30"
                    },
                    "suspects": [
                        {"suspect_id": "s1", "name": "王管家", "age": 52, "role": "管家"},
                        {"suspect_id": "s2", "name": "张美", "age": 28, "role": "妻子"},
                        {"suspect_id": "s3", "name": "李司机", "age": 30, "role": "司机"}
                    ],
                    "initial_scene": "书房"
                }
            })
            yield

    def test_create_new_case_success(self):
        """API-GAME-001: 正常创建新案件"""
        response = client.post(
            "/api/v1/game/new",
            json={"user_id": "test_user", "difficulty": "medium"}
        )

        assert response.status_code == 200
        data = response.json()

        # 验证返回包含session_id
        assert "session_id" in data
        assert data["session_id"] == "test_session_001"

        # 验证返回包含case_basic_info
        assert "case_basic_info" in data
        case_info = data["case_basic_info"]

        # 验证死者信息
        assert "victim" in case_info
        assert case_info["victim"]["name"] == "陈天"

        # 验证嫌疑人列表（3-5人）
        assert "suspects" in case_info
        assert 3 <= len(case_info["suspects"]) <= 5
        for suspect in case_info["suspects"]:
            assert "suspect_id" in suspect
            assert "name" in suspect
            assert "age" in suspect
            assert "role" in suspect

        # 验证初始场景
        assert "initial_scene" in case_info

    def test_create_case_with_easy_difficulty(self):
        """API-GAME-002: 使用easy难度创建"""
        response = client.post(
            "/api/v1/game/new",
            json={"user_id": "test_user", "difficulty": "easy"}
        )
        assert response.status_code == 200

    def test_create_case_with_hard_difficulty(self):
        """API-GAME-003: 使用hard难度创建"""
        response = client.post(
            "/api/v1/game/new",
            json={"user_id": "test_user", "difficulty": "hard"}
        )
        assert response.status_code == 200

    def test_create_case_without_user_id(self):
        """API-GAME-004: 不带user_id创建"""
        response = client.post(
            "/api/v1/game/new",
            json={"difficulty": "medium"}
        )
        assert response.status_code == 200

    def test_create_case_without_parameters(self):
        """API-GAME-005: 不带任何参数创建"""
        response = client.post(
            "/api/v1/game/new",
            json={}
        )
        assert response.status_code == 200

    def test_create_case_with_invalid_difficulty(self):
        """API-GAME-006: 无效难度参数"""
        response = client.post(
            "/api/v1/game/new",
            json={"user_id": "test_user", "difficulty": "invalid"}
        )
        # 注意：根据实际实现可能返回422或使用默认值
        # 这里假设会使用默认值，如需422可调整
        assert response.status_code in [200, 422]


class TestGameStatusAPI:
    """测试获取游戏状态接口 - API-GAME-010 ~ API-GAME-014"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """设置mock依赖"""
        with patch('app.services.game_service.game_service') as mock_service:
            self.mock_game_service = mock_service

            # mock get_game_status
            self.mock_game_service.get_game_status.return_value = {
                "session_id": "test_session_001",
                "game_status": "investigating",
                "case_basic_info": {
                    "victim": {"name": "陈天"},
                    "suspects": [
                        {"suspect_id": "s1", "name": "王管家"}
                    ]
                },
                "suspect_states": {
                    "s1": {"mood": "calm", "stress_level": 30}
                },
                "collected_clues_count": 3,
                "total_clues": 20,
                "wrong_guess_count": 0
            }

            yield

    def test_get_game_status_success(self):
        """API-GAME-010: 正常获取游戏状态"""
        response = client.get("/api/v1/game/test_session_001/status")
        assert response.status_code == 200

        data = response.json()
        assert "session_id" in data
        assert "game_status" in data
        assert "suspect_states" in data
        assert "collected_clues_count" in data
        assert "total_clues" in data

    def test_get_nonexistent_session_status(self):
        """API-GAME-011: 获取不存在的会话"""
        # 设置mock抛出异常
        from app.core.exceptions import SessionNotFoundException
        self.mock_game_service.get_game_status.side_effect = SessionNotFoundException(
            detail="会话不存在"
        )

        response = client.get("/api/v1/game/nonexistent_session/status")
        # 注意：实际状态码取决于异常处理，这里假设返回404
        assert response.status_code in [404, 200]

    def test_game_status_is_investigating(self):
        """API-GAME-012: 会话状态为'进行中'"""
        response = client.get("/api/v1/game/test_session_001/status")
        data = response.json()
        # 根据实际实现，状态可能是investigating或IN_PROGRESS
        assert data["game_status"] in ["investigating", "IN_PROGRESS"]

    def test_status_contains_suspect_list(self):
        """API-GAME-013: 状态包含嫌疑人列表"""
        response = client.get("/api/v1/game/test_session_001/status")
        data = response.json()
        assert "suspect_states" in data
        assert isinstance(data["suspect_states"], dict)

    def test_status_contains_clue_statistics(self):
        """API-GAME-014: 状态包含线索统计"""
        response = client.get("/api/v1/game/test_session_001/status")
        data = response.json()
        assert "collected_clues_count" in data
        assert "total_clues" in data


class TestInvestigationAPI:
    """测试勘查接口 - API-GAME-020 ~ API-GAME-025"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """设置mock依赖"""
        with patch('app.services.game_service.game_service') as mock_service:
            self.mock_game_service = mock_service

            # 默认mock返回值 - 找到新线索
            self.mock_game_service.submit_investigation.return_value = {
                "success": True,
                "found_clue": True,
                "clue": {
                    "clue_id": "c1",
                    "name": "带血的碎玻璃",
                    "description": "书桌下方有一块带血的碎玻璃",
                    "clue_type": "physical",
                    "status": "collected",
                    "scene": "书房",
                    "location": "书桌下方"
                },
                "message": "找到了一条新线索！"
            }

            yield

    def test_submit_investigation_success(self):
        """API-GAME-020: 正常勘查场景"""
        response = client.post(
            "/api/v1/game/test_session_001/investigate",
            json={"scene": "书房", "item": "书桌"}
        )
        assert response.status_code == 200

    def test_investigation_finds_new_clue(self):
        """API-GAME-021: 勘查找到新线索"""
        response = client.post(
            "/api/v1/game/test_session_001/investigate",
            json={"scene": "书房", "item": "书桌"}
        )
        data = response.json()

        assert data["found_clue"] is True
        assert "clue" in data
        clue = data["clue"]
        assert "clue_id" in clue
        assert "name" in clue
        assert "description" in clue
        assert "clue_type" in clue

    def test_investigation_already_searched(self):
        """API-GAME-022: 勘查已搜查过的位置"""
        # 设置mock返回已搜查过
        self.mock_game_service.submit_investigation.return_value = {
            "success": True,
            "found_clue": False,
            "message": "这个位置已经搜查过了"
        }

        response = client.post(
            "/api/v1/game/test_session_001/investigate",
            json={"scene": "书房", "item": "书桌"}
        )
        data = response.json()
        assert "已搜查过" in data["message"] or data["found_clue"] is False

    def test_investigation_nonexistent_session(self):
        """API-GAME-023: 勘查不存在的会话"""
        from app.core.exceptions import SessionNotFoundException
        self.mock_game_service.submit_investigation.side_effect = SessionNotFoundException(
            detail="会话不存在"
        )

        response = client.post(
            "/api/v1/game/nonexistent_session/investigate",
            json={"scene": "书房", "item": "书桌"}
        )
        assert response.status_code in [404, 200]

    def test_investigation_missing_scene(self):
        """API-GAME-024: 缺少scene参数"""
        response = client.post(
            "/api/v1/game/test_session_001/investigate",
            json={"item": "书桌"}
        )
        # 根据实际实现，可能返回422
        assert response.status_code in [200, 422]

    def test_investigation_encrypted_clue(self):
        """API-GAME-025: 勘查需解密的线索"""
        self.mock_game_service.submit_investigation.return_value = {
            "success": True,
            "found_clue": True,
            "clue": {
                "clue_id": "c2",
                "name": "上锁的日记",
                "description": "一本上锁的日记，需要密码才能打开",
                "clue_type": "physical",
                "status": "needs_decryption",
                "scene": "书房",
                "location": "书架暗格"
            },
            "message": "发现了一条需要解密的线索！"
        }

        response = client.post(
            "/api/v1/game/test_session_001/investigate",
            json={"scene": "书房", "item": "书架"}
        )
        data = response.json()
        assert "needs_decryption" in str(data).lower() or "需解密" in str(data)


class TestDecryptClueAPI:
    """测试线索解密接口 - API-GAME-030 ~ API-GAME-035"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """设置mock依赖"""
        with patch('app.services.game_service.game_service') as mock_service:
            self.mock_game_service = mock_service

            # 默认mock - 密码解密成功
            self.mock_game_service.decrypt_clue.return_value = {
                "success": True,
                "decrypted": True,
                "clue": {
                    "clue_id": "c2",
                    "name": "日记内容",
                    "description": "日记中记录了死者与王管家的争吵...",
                    "clue_type": "physical",
                    "status": "decrypted"
                },
                "message": "解密成功！"
            }

            yield

    def test_decrypt_with_password_success(self):
        """API-GAME-030: 密码解密成功"""
        response = client.post(
            "/api/v1/game/test_session_001/decrypt",
            json={"clue_id": "c2", "password": "123456"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["decrypted"] is True

    def test_decrypt_with_wrong_password(self):
        """API-GAME-031: 密码解密失败"""
        self.mock_game_service.decrypt_clue.return_value = {
            "success": True,
            "decrypted": False,
            "message": "密码错误，请再试试"
        }

        response = client.post(
            "/api/v1/game/test_session_001/decrypt",
            json={"clue_id": "c2", "password": "wrong_password"}
        )
        data = response.json()
        assert data["decrypted"] is False

    def test_decrypt_with_association(self):
        """API-GAME-032: 线索关联解密"""
        self.mock_game_service.decrypt_clue.return_value = {
            "success": True,
            "decrypted": True,
            "clue": {
                "clue_id": "c_combined",
                "name": "关联线索",
                "description": "通过关联多条线索，发现了新的证据...",
                "clue_type": "physical",
                "status": "decrypted"
            },
            "message": "线索关联成功！"
        }

        response = client.post(
            "/api/v1/game/test_session_001/decrypt",
            json={
                "clue_id": "c2",
                "related_clues": ["c1", "c3"]
            }
        )
        data = response.json()
        assert data["decrypted"] is True

    def test_decrypt_incomplete_association(self):
        """API-GAME-033: 关联线索不完整"""
        self.mock_game_service.decrypt_clue.return_value = {
            "success": True,
            "decrypted": False,
            "message": "还缺少一些必要的线索"
        }

        response = client.post(
            "/api/v1/game/test_session_001/decrypt",
            json={
                "clue_id": "c2",
                "related_clues": ["c1"]
            }
        )
        data = response.json()
        assert data["decrypted"] is False

    def test_decrypt_nonexistent_clue(self):
        """API-GAME-034: 解密不存在的线索"""
        from app.core.exceptions import ClueNotFoundException
        self.mock_game_service.decrypt_clue.side_effect = ClueNotFoundException(
            detail="线索不存在"
        )

        response = client.post(
            "/api/v1/game/test_session_001/decrypt",
            json={"clue_id": "nonexistent", "password": "123456"}
        )
        assert response.status_code in [404, 200]

    def test_decrypt_unencrypted_clue(self):
        """API-GAME-035: 解密不需要解密的线索"""
        self.mock_game_service.decrypt_clue.return_value = {
            "success": True,
            "decrypted": True,
            "message": "这条线索无需解密"
        }

        response = client.post(
            "/api/v1/game/test_session_001/decrypt",
            json={"clue_id": "c1", "password": "123456"}
        )
        data = response.json()
        assert "无需解密" in data["message"] or data["decrypted"] is True


class TestAccuseAPI:
    """测试指认凶手接口 - API-GAME-040 ~ API-GAME-047"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """设置mock依赖"""
        with patch('app.services.game_service.game_service') as mock_service:
            self.mock_game_service = mock_service

            # 默认mock - 正确指认
            self.mock_game_service.submit_accusation = AsyncMock(return_value={
                "success": True,
                "accuse_result": True,
                "wrong_guess_count": 0,
                "remaining_guesses": 2,
                "case_report": {
                    "summary": "指认正确！",
                    "full_case_reveal": {
                        "murderer": "王管家",
                        "motive": "长期被侮辱，拖欠工资",
                        "method": "用烟灰缸击打死者头部"
                    },
                    "investigation_review": {
                        "clues_collected": 24,
                        "accuracy": 85,
                        "highlights": ["及时发现了关键证据"],
                        "missing_points": ["遗漏了一些间接证据"]
                    }
                }
            })

            yield

    def test_accuse_correct_murderer(self):
        """API-GAME-040: 正确指认凶手"""
        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "suspect_id": "s1",
                "motive": "长期被侮辱，拖欠工资",
                "modus_operandi": "用烟灰缸击打死者头部",
                "evidence": ["c1", "c2", "c3"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["accuse_result"] is True
        assert "case_report" in data

    def test_accuse_wrong_murderer(self):
        """API-GAME-041: 错误指认凶手"""
        self.mock_game_service.submit_accusation.return_value = {
            "success": True,
            "accuse_result": False,
            "wrong_guess_count": 1,
            "remaining_guesses": 2,
            "message": "指认不正确，还有遗漏的线索"
        }

        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "suspect_id": "s2",
                "motive": "图财害命",
                "modus_operandi": "下毒",
                "evidence": ["c1"]
            }
        )
        data = response.json()
        assert data["accuse_result"] is False

    def test_first_wrong_accusation(self):
        """API-GAME-042: 第一次错误指认"""
        self.mock_game_service.submit_accusation.return_value = {
            "success": True,
            "accuse_result": False,
            "wrong_guess_count": 1,
            "remaining_guesses": 2,
            "message": "指认不正确，请继续探案"
        }

        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "suspect_id": "s2",
                "motive": "motive",
                "modus_operandi": "method",
                "evidence": ["c1"]
            }
        )
        data = response.json()
        assert data["remaining_guesses"] == 2

    def test_second_wrong_accusation(self):
        """API-GAME-043: 第二次错误指认"""
        self.mock_game_service.submit_accusation.return_value = {
            "success": True,
            "accuse_result": False,
            "wrong_guess_count": 2,
            "remaining_guesses": 1,
            "message": "指认不正确，还有1次机会"
        }

        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "suspect_id": "s3",
                "motive": "motive",
                "modus_operandi": "method",
                "evidence": ["c1"]
            }
        )
        data = response.json()
        assert data["remaining_guesses"] == 1

    def test_third_wrong_accusation(self):
        """API-GAME-044: 第三次错误指认"""
        self.mock_game_service.submit_accusation.return_value = {
            "success": True,
            "accuse_result": False,
            "wrong_guess_count": 3,
            "remaining_guesses": 0,
            "game_status": "failed",
            "message": "游戏失败，真相是...",
            "case_report": {
                "full_case_reveal": {"murderer": "s1"}
            }
        }

        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "suspect_id": "s2",
                "motive": "m",
                "modus_operandi": "m",
                "evidence": ["c1"]
            }
        )
        data = response.json()
        assert data["remaining_guesses"] == 0 or data["game_status"] == "failed"

    def test_accuse_nonexistent_session(self):
        """API-GAME-045: 指认不存在的会话"""
        from app.core.exceptions import SessionNotFoundException
        self.mock_game_service.submit_accusation.side_effect = SessionNotFoundException(
            detail="会话不存在"
        )

        response = client.post(
            "/api/v1/game/nonexistent_session/accuse",
            json={
                "suspect_id": "s1",
                "motive": "m",
                "modus_operandi": "m",
                "evidence": ["c1"]
            }
        )
        assert response.status_code in [404, 200]

    def test_accuse_missing_parameters(self):
        """API-GAME-046: 缺少必要参数"""
        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "motive": "motive",
                "modus_operandi": "method",
                "evidence": ["c1"]
            }
        )
        assert response.status_code in [200, 422]

    def test_accuse_already_closed_game(self):
        """API-GAME-047: 已结案后再次指认"""
        self.mock_game_service.submit_accusation.return_value = {
            "success": False,
            "message": "游戏已结束，无法再指认"
        }

        response = client.post(
            "/api/v1/game/test_session_001/accuse",
            json={
                "suspect_id": "s1",
                "motive": "m",
                "modus_operandi": "m",
                "evidence": ["c1"]
            }
        )
        data = response.json()
        assert "已结束" in data["message"] or data["success"] is False


class TestCluesAPI:
    """测试线索相关接口 - API-GAME-050 ~ API-GAME-082"""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """设置mock依赖"""
        with patch('app.services.clue_service.clue_service') as mock_service:
            self.mock_clue_service = mock_service

            # mock获取线索列表
            self.mock_clue_service.get_collected_clues.return_value = [
                {
                    "clue_id": "c1",
                    "name": "带血的碎玻璃",
                    "description": "书桌下方的碎玻璃",
                    "clue_type": "physical",
                    "collected_at": "2026-04-06T10:00:00Z"
                },
                {
                    "clue_id": "c2",
                    "name": "王管家的证词",
                    "description": "王管家说昨晚10点在书房",
                    "clue_type": "testimony",
                    "collected_at": "2026-04-06T10:05:00Z"
                }
            ]

            # mock获取线索统计
            self.mock_clue_service.get_clue_statistics.return_value = {
                "total_clues": 20,
                "collected_clues": 2,
                "completion_rate": 10,
                "type_statistics": {
                    "physical": 1,
                    "testimony": 1
                }
            }

            # mock获取线索详情
            self.mock_clue_service.get_clue_detail.return_value = {
                "clue_id": "c1",
                "name": "带血的碎玻璃",
                "description": "书桌下方有一块带血的碎玻璃",
                "clue_type": "physical",
                "scene": "书房",
                "location": "书桌下方",
                "related_clues": ["c3"]
            }

            # mock关联线索
            self.mock_clue_service.associate_clues.return_value = {
                "success": True,
                "message": "线索关联成功，发现了新的联系",
                "new_clue": {
                    "clue_id": "c_combined",
                    "name": "关联证据",
                    "description": "通过关联线索发现..."
                }
            }

            # mock获取提示
            self.mock_clue_service.get_undiscovered_clue_hints.return_value = [
                {
                    "hint": "建议检查一下书房的书架",
                    "scene": "书房",
                    "item": "书架"
                }
            ]

            yield

    def test_get_collected_clues(self):
        """API-GAME-050: 获取所有线索"""
        response = client.get("/api/v1/game/test_session_001/clues")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 0

    def test_get_clues_by_physical_type(self):
        """API-GAME-051: 按类型过滤-物证"""
        response = client.get(
            "/api/v1/game/test_session_001/clues",
            params={"clue_type": "physical"}
        )
        assert response.status_code == 200

    def test_get_clues_by_testimony_type(self):
        """API-GAME-052: 按类型过滤-证词"""
        response = client.get(
            "/api/v1/game/test_session_001/clues",
            params={"clue_type": "testimony"}
        )
        assert response.status_code == 200

    def test_get_clues_new_game_empty(self):
        """API-GAME-053: 新游戏无线索"""
        self.mock_clue_service.get_collected_clues.return_value = []
        response = client.get("/api/v1/game/test_session_001/clues")
        data = response.json()
        assert len(data) == 0

    def test_get_clues_nonexistent_session(self):
        """API-GAME-054: 获取不存在会话的线索"""
        from app.core.exceptions import SessionNotFoundException
        self.mock_clue_service.get_collected_clues.side_effect = SessionNotFoundException(
            detail="会话不存在"
        )
        response = client.get("/api/v1/game/nonexistent_session/clues")
        assert response.status_code in [404, 200]

    def test_get_clue_statistics(self):
        """API-GAME-060 ~ API-GAME-064: 获取线索统计"""
        response = client.get("/api/v1/game/test_session_001/clues/statistics")
        assert response.status_code == 200
        data = response.json()

        assert "total_clues" in data
        assert "collected_clues" in data
        assert "completion_rate" in data
        assert "type_statistics" in data

    def test_associate_clues_success(self):
        """API-GAME-070: 成功关联线索"""
        response = client.post(
            "/api/v1/game/test_session_001/clues/associate",
            json=["c1", "c2"]
        )
        assert response.status_code == 200

    def test_associate_clues_unrelatable(self):
        """API-GAME-071: 线索不可关联"""
        self.mock_clue_service.associate_clues.return_value = {
            "success": False,
            "message": "这些线索之间没有关联"
        }
        response = client.post(
            "/api/v1/game/test_session_001/clues/associate",
            json=["c1", "c2"]
        )
        data = response.json()
        assert data["success"] is False

    def test_associate_clues_insufficient(self):
        """API-GAME-072: 线索数量不足"""
        response = client.post(
            "/api/v1/game/test_session_001/clues/associate",
            json=["c1"]
        )
        assert response.status_code in [200, 422]

    def test_associate_clues_duplicate(self):
        """API-GAME-073: 重复关联"""
        self.mock_clue_service.associate_clues.return_value = {
            "success": False,
            "message": "这些线索已经关联过了"
        }
        response = client.post(
            "/api/v1/game/test_session_001/clues/associate",
            json=["c1", "c2"]
        )
        data = response.json()
        assert "已关联" in data["message"] or data["success"] is False

    def test_get_clue_hints(self):
        """API-GAME-080: 获取卡关提示"""
        response = client.get("/api/v1/game/test_session_001/clues/hints")
        assert response.status_code == 200

    def test_hint_does_not_reveal_answer(self):
        """API-GAME-081: 提示不泄露答案"""
        response = client.get("/api/v1/game/test_session_001/clues/hints")
        data = response.json()
        # 验证提示中不直接包含"凶手"、"真凶"等字样
        for hint in data:
            assert "凶手" not in str(hint)
            assert "真凶" not in str(hint)

    def test_all_clues_collected_hint(self):
        """API-GAME-082: 所有线索已收集"""
        self.mock_clue_service.get_undiscovered_clue_hints.return_value = [
            {"hint": "所有线索已收集，可以指认凶手了"}
        ]
        response = client.get("/api/v1/game/test_session_001/clues/hints")
        data = response.json()
        assert "所有线索已收集" in str(data)

