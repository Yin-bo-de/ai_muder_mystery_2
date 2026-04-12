"""对话历史分离存储单元测试"""
import pytest
from datetime import datetime
from app.models.agent import Message, MessageRole, DialogueMode
from app.models.case import Case, Victim, Suspect, Scene
from app.core.constants import GameStatus
from app.services.session_service import session_service


@pytest.fixture
def mock_case():
    """创建模拟案件数据"""
    return Case(
        case_id="test_case_001",
        title="测试案件",
        description="这是一个测试案件",
        difficulty=2,
        theme="modern",
        victim=Victim(
            victim_id="v1",
            name="张三",
            age=45,
            gender="男",
            occupation="公司老板",
            description="中等身材，性格强势",
            cause_of_death="锐器刺伤",
            death_time=datetime(2026, 4, 6, 14, 30, 0),
            death_location="张三的办公室",
            social_relationships={},
            background_story="",
        ),
        suspects=[
            Suspect(
                suspect_id="s1",
                name="李四",
                age=32,
                gender="男",
                occupation="外卖员",
                description="",
                personality_traits=[],
                relationship_with_victim="债主",
                motive="",
                alibi="",
                alibi_reliability=0.6,
                timeline={},
                secrets=[],
                is_murderer=True,
                background_story="",
            ),
            Suspect(
                suspect_id="s2",
                name="王五",
                age=28,
                gender="男",
                occupation="公司职员",
                description="",
                personality_traits=[],
                relationship_with_victim="同事",
                motive="",
                alibi="",
                alibi_reliability=0.8,
                timeline={},
                secrets=[],
                is_murderer=False,
                background_story="",
            ),
        ],
        clues=[],
        scenes=[],
        evidence_chains=[],
        murderer_id="s1",
        murder_weapon="",
        murder_motive="",
        murder_method="",
        true_timeline={},
        red_herrings=[],
    )


@pytest.fixture
def test_session(mock_case):
    """创建测试会话"""
    session = session_service.create_session("test_user", mock_case)
    yield session
    # 清理
    session_service.delete_session(session.session_id)


class TestMessageModel:
    """测试 Message 模型新增字段"""

    def test_message_dialogue_mode_field(self):
        """测试 dialogue_mode 字段"""
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="测试消息",
            dialogue_mode=DialogueMode.GROUP,
        )
        assert msg.dialogue_mode == DialogueMode.GROUP

        msg2 = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="单独审讯消息",
            dialogue_mode=DialogueMode.SINGLE,
        )
        assert msg2.dialogue_mode == DialogueMode.SINGLE

    def test_message_single_interrogation_target_field(self):
        """测试 single_interrogation_target 字段"""
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="测试消息",
            dialogue_mode=DialogueMode.SINGLE,
            single_interrogation_target="s1",
        )
        assert msg.single_interrogation_target == "s1"

    def test_message_fields_optional(self):
        """测试新增字段是可选的（向后兼容）"""
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="测试消息",
        )
        assert msg.dialogue_mode is None
        assert msg.single_interrogation_target is None


class TestSessionServiceSeparateStorage:
    """测试 SessionService 分离存储功能"""

    def test_group_message_stored_in_group_history(self, test_session):
        """测试全体质询模式消息存储到 group_dialogue_history"""
        session_id = test_session.session_id

        # 添加一条全体质询模式的消息
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="大家好，我是侦探",
        )

        result = session_service.add_dialogue_message(
            session_id,
            msg,
            dialogue_mode=DialogueMode.GROUP,
        )

        assert result is True

        # 验证消息存储在正确的位置
        updated_session = session_service.get_session(session_id)
        assert len(updated_session.dialogue_history) == 1  # 完整历史
        assert len(updated_session.group_dialogue_history) == 1  # 全体历史
        assert len(updated_session.single_dialogue_histories) == 0  # 单独审讯历史为空

        # 验证消息内容
        stored_msg = updated_session.group_dialogue_history[0]
        assert stored_msg.content == "大家好，我是侦探"
        assert stored_msg.dialogue_mode == DialogueMode.GROUP

    def test_single_message_stored_in_suspect_history(self, test_session):
        """测试单独审讯模式消息存储到对应嫌疑人的历史"""
        session_id = test_session.session_id

        # 添加一条针对 s1 的单独审讯消息
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="李四，说说你的不在场证明",
        )

        result = session_service.add_dialogue_message(
            session_id,
            msg,
            dialogue_mode=DialogueMode.SINGLE,
            single_interrogation_target="s1",
        )

        assert result is True

        # 验证消息存储在正确的位置
        updated_session = session_service.get_session(session_id)
        assert len(updated_session.dialogue_history) == 1  # 完整历史
        assert len(updated_session.group_dialogue_history) == 0  # 全体历史为空
        assert "s1" in updated_session.single_dialogue_histories
        assert len(updated_session.single_dialogue_histories["s1"]) == 1

        # 验证消息内容
        stored_msg = updated_session.single_dialogue_histories["s1"][0]
        assert stored_msg.content == "李四，说说你的不在场证明"
        assert stored_msg.dialogue_mode == DialogueMode.SINGLE
        assert stored_msg.single_interrogation_target == "s1"

    def test_multiple_suspects_single_histories(self, test_session):
        """测试多个嫌疑人的单独审讯历史分别存储"""
        session_id = test_session.session_id

        # 给 s1 添加消息
        msg1 = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="李四的问题",
        )
        session_service.add_dialogue_message(
            session_id, msg1, DialogueMode.SINGLE, "s1"
        )

        # 给 s2 添加消息
        msg2 = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="王五的问题",
        )
        session_service.add_dialogue_message(
            session_id, msg2, DialogueMode.SINGLE, "s2"
        )

        # 再给 s1 添加一条消息
        msg3 = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="李四的另一个问题",
        )
        session_service.add_dialogue_message(
            session_id, msg3, DialogueMode.SINGLE, "s1"
        )

        updated_session = session_service.get_session(session_id)

        # 验证完整历史有3条
        assert len(updated_session.dialogue_history) == 3

        # 验证 s1 有2条
        assert len(updated_session.single_dialogue_histories["s1"]) == 2
        # 验证 s2 有1条
        assert len(updated_session.single_dialogue_histories["s2"]) == 1

    def test_mixed_mode_storage(self, test_session):
        """测试混合模式存储"""
        session_id = test_session.session_id

        # 全体质询消息
        msg_group = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="大家都说说",
        )
        session_service.add_dialogue_message(
            session_id, msg_group, DialogueMode.GROUP
        )

        # 单独审讯 s1
        msg_single = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="李四，你来说",
        )
        session_service.add_dialogue_message(
            session_id, msg_single, DialogueMode.SINGLE, "s1"
        )

        updated_session = session_service.get_session(session_id)

        # 完整历史有2条
        assert len(updated_session.dialogue_history) == 2
        # 全体历史有1条
        assert len(updated_session.group_dialogue_history) == 1
        # s1 单独历史有1条
        assert len(updated_session.single_dialogue_histories["s1"]) == 1

    def test_backward_compatibility_full_history(self, test_session):
        """测试向后兼容：旧的调用方式仍然可以工作"""
        session_id = test_session.session_id

        # 使用旧的调用方式（不传 mode 和 target）
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="旧方式的消息",
        )
        result = session_service.add_dialogue_message(session_id, msg)

        assert result is True

        updated_session = session_service.get_session(session_id)
        assert len(updated_session.dialogue_history) == 1
        # 消息的 mode 字段为 None
        assert updated_session.dialogue_history[0].dialogue_mode is None


class TestSessionServiceRelevantHistory:
    """测试 SessionService 筛选查询功能"""

    def test_get_relevant_history_group_mode(self, test_session):
        """测试全体质询模式获取相关历史"""
        session_id = test_session.session_id

        # 添加全体历史消息
        for i in range(3):
            msg = Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content=f"全体消息 {i}",
            )
            session_service.add_dialogue_message(
                session_id, msg, DialogueMode.GROUP
            )

        # 添加单独审讯消息（不应该被返回）
        msg_single = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="单独消息",
        )
        session_service.add_dialogue_message(
            session_id, msg_single, DialogueMode.SINGLE, "s1"
        )

        # 获取全体模式相关历史
        relevant_history = session_service.get_relevant_dialogue_history(
            session_id, DialogueMode.GROUP
        )

        assert len(relevant_history) == 3
        assert all("全体消息" in msg.content for msg in relevant_history)

    def test_get_relevant_history_single_mode(self, test_session):
        """测试单独审讯模式获取相关历史"""
        session_id = test_session.session_id

        # 给 s1 添加消息
        for i in range(2):
            msg = Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content=f"给 s1 的消息 {i}",
            )
            session_service.add_dialogue_message(
                session_id, msg, DialogueMode.SINGLE, "s1"
            )

        # 给 s2 添加消息（不应该被返回）
        msg_s2 = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="给 s2 的消息",
        )
        session_service.add_dialogue_message(
            session_id, msg_s2, DialogueMode.SINGLE, "s2"
        )

        # 添加全体历史消息（不应该被返回）
        msg_group = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="全体消息",
        )
        session_service.add_dialogue_message(
            session_id, msg_group, DialogueMode.GROUP
        )

        # 获取 s1 单独审讯相关历史
        relevant_history = session_service.get_relevant_dialogue_history(
            session_id, DialogueMode.SINGLE, "s1"
        )

        assert len(relevant_history) == 2
        assert all("给 s1 的消息" in msg.content for msg in relevant_history)

    def test_get_relevant_history_nonexistent_suspect(self, test_session):
        """测试获取不存在嫌疑人的历史返回空列表"""
        session_id = test_session.session_id

        # 添加一些消息
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="测试消息",
        )
        session_service.add_dialogue_message(
            session_id, msg, DialogueMode.SINGLE, "s1"
        )

        # 获取不存在的嫌疑人历史
        relevant_history = session_service.get_relevant_dialogue_history(
            session_id, DialogueMode.SINGLE, "nonexistent"
        )

        assert len(relevant_history) == 0

    def test_get_relevant_history_uses_session_current_mode(self, test_session):
        """测试不传 mode 参数时使用会话当前模式"""
        session_id = test_session.session_id
        session = session_service.get_session(session_id)

        # 设置会话当前模式为单独审讯 s1
        session.current_mode = DialogueMode.SINGLE
        session.target_suspect = "s1"
        session_service.update_session(session)

        # 添加 s1 的单独审讯消息
        msg = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="给 s1 的消息",
        )
        session_service.add_dialogue_message(
            session_id, msg, DialogueMode.SINGLE, "s1"
        )

        # 不传 mode 参数，应该使用会话当前模式
        relevant_history = session_service.get_relevant_dialogue_history(session_id)

        assert len(relevant_history) == 1
        assert relevant_history[0].content == "给 s1 的消息"


class TestClearDialogueHistory:
    """测试清空对话历史功能"""

    def test_clear_all_histories(self, test_session):
        """测试清空所有历史字段"""
        session_id = test_session.session_id

        # 添加各种历史消息
        msg_group = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="全体消息",
        )
        session_service.add_dialogue_message(
            session_id, msg_group, DialogueMode.GROUP
        )

        msg_single = Message(
            role=MessageRole.USER,
            sender_id="user",
            sender_name="用户",
            content="单独消息",
        )
        session_service.add_dialogue_message(
            session_id, msg_single, DialogueMode.SINGLE, "s1"
        )

        # 导入 dialogue_service 来清空历史
        from app.services.dialogue_service import dialogue_service

        result = dialogue_service.clear_dialogue_history(session_id)
        assert result is True

        # 验证所有历史都被清空
        updated_session = session_service.get_session(session_id)
        assert len(updated_session.dialogue_history) == 0
        assert len(updated_session.group_dialogue_history) == 0
        assert len(updated_session.single_dialogue_histories) == 0


class TestDialogueManagerHistoryFiltering:
    """测试 DialogueManager 历史筛选逻辑"""

    def test_filter_group_mode_history_filtering(self):
        """测试全体质询模式下的历史筛选"""
        from app.agents.dialogue_manager import DialogueManager
        from app.models.case import Suspect
        from app.core.constants import DialogueMode

        # 创建模拟嫌疑人
        suspects = [
            Suspect(
                suspect_id="s1",
                name="李四",
                age=32,
                gender="男",
                occupation="外卖员",
                description="",
                personality_traits=[],
                relationship_with_victim="债主",
                motive="",
                alibi="",
                alibi_reliability=0.6,
                timeline={},
                secrets=[],
                is_murderer=True,
                background_story="",
            ),
            Suspect(
                suspect_id="s2",
                name="王五",
                age=28,
                gender="男",
                occupation="公司职员",
                description="",
                personality_traits=[],
                relationship_with_victim="同事",
                motive="",
                alibi="",
                alibi_reliability=0.8,
                timeline={},
                secrets=[],
                is_murderer=False,
                background_story="",
            ),
        ]

        # 创建 DialogueManager（禁用意图识别Agent）
        from unittest.mock import patch, MagicMock
        with patch('app.core.config.settings.ENABLE_INTENT_RECOGNITION_AGENT', True):
            manager = DialogueManager(suspects, "s1")
            # Mock intent_recognition_agent 避免LLM调用
            manager.intent_recognition_agent = MagicMock()
            from app.agents.intent_recognition_agent import IntentRecognitionResult, UserIntent
            manager.intent_recognition_agent.analyze = MagicMock(return_value=IntentRecognitionResult(
                intent_type=UserIntent.ALL,
                target_suspect_ids=["s1", "s2"],
                confidence=1.0,
                reasoning="测试"
            ))

        # 设置为全体质询模式
        manager.dialogue_mode = DialogueMode.GROUP

        # 创建混合历史
        from app.models.agent import Message, MessageRole
        dialogue_history = [
            # 全体质询模式消息（应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="大家好",
                dialogue_mode=DialogueMode.GROUP,
            ),
            # 单独审讯消息（不应该被筛选出来）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="单独审讯的问题",
                dialogue_mode=DialogueMode.SINGLE,
                single_interrogation_target="s1",
            ),
            # 另一条全体质询消息（应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="谁是凶手？",
                dialogue_mode=DialogueMode.GROUP,
            ),
            # 旧消息（dialogue_mode为None，应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="旧消息",
                dialogue_mode=None,
            ),
        ]

        # 调用 _analyze_user_intent_with_context
        import asyncio
        result = asyncio.run(manager._analyze_user_intent_with_context(
            "测试问题",
            dialogue_history
        ))

        # 验证 intent_recognition_agent 被调用时传入的是筛选后的历史
        call_args = manager.intent_recognition_agent.analyze.call_args
        assert call_args is not None
        passed_history = call_args[1]['dialogue_history']
        assert len(passed_history) == 3  # 2条GROUP + 1条None
        assert all(msg.content != "单独审讯的问题" for msg in passed_history)

    def test_single_mode_history_filtering(self):
        """测试单独审讯模式下的历史筛选"""
        from app.agents.dialogue_manager import DialogueManager
        from app.models.case import Suspect
        from app.core.constants import DialogueMode

        # 创建模拟嫌疑人
        suspects = [
            Suspect(
                suspect_id="s1",
                name="李四",
                age=32,
                gender="男",
                occupation="外卖员",
                description="",
                personality_traits=[],
                relationship_with_victim="债主",
                motive="",
                alibi="",
                alibi_reliability=0.6,
                timeline={},
                secrets=[],
                is_murderer=True,
                background_story="",
            ),
            Suspect(
                suspect_id="s2",
                name="王五",
                age=28,
                gender="男",
                occupation="公司职员",
                description="",
                personality_traits=[],
                relationship_with_victim="同事",
                motive="",
                alibi="",
                alibi_reliability=0.8,
                timeline={},
                secrets=[],
                is_murderer=False,
                background_story="",
            ),
        ]

        # 创建 DialogueManager
        from unittest.mock import patch, MagicMock
        with patch('app.core.config.settings.ENABLE_INTENT_RECOGNITION_AGENT', True):
            manager = DialogueManager(suspects, "s1")
            # Mock intent_recognition_agent
            manager.intent_recognition_agent = MagicMock()
            from app.agents.intent_recognition_agent import IntentRecognitionResult, UserIntent
            manager.intent_recognition_agent.analyze = MagicMock(return_value=IntentRecognitionResult(
                intent_type=UserIntent.SINGLE,
                target_suspect_ids=["s1"],
                confidence=1.0,
                reasoning="测试"
            ))

        # 设置为单独审讯模式（针对s1）
        manager.dialogue_mode = DialogueMode.SINGLE
        manager.current_interrogation_suspect = "s1"

        # 创建混合历史
        from app.models.agent import Message, MessageRole
        dialogue_history = [
            # s1的单独审讯消息（应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="给s1的问题1",
                dialogue_mode=DialogueMode.SINGLE,
                single_interrogation_target="s1",
            ),
            # s2的单独审讯消息（不应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="给s2的问题",
                dialogue_mode=DialogueMode.SINGLE,
                single_interrogation_target="s2",
            ),
            # 另一条s1的单独审讯消息（应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="给s1的问题2",
                dialogue_mode=DialogueMode.SINGLE,
                single_interrogation_target="s1",
            ),
            # 全体质询消息（不应该保留）
            Message(
                role=MessageRole.USER,
                sender_id="user",
                sender_name="用户",
                content="全体消息",
                dialogue_mode=DialogueMode.GROUP,
            ),
        ]

        # 调用 _analyze_user_intent_with_context
        import asyncio
        result = asyncio.run(manager._analyze_user_intent_with_context(
            "测试问题",
            dialogue_history
        ))

        # 验证 intent_recognition_agent 被调用时传入的是筛选后的历史
        call_args = manager.intent_recognition_agent.analyze.call_args
        assert call_args is not None
        passed_history = call_args[1]['dialogue_history']
        assert len(passed_history) == 2
        assert all(msg.content.startswith("给s1的问题") for msg in passed_history)
        assert all(msg.single_interrogation_target == "s1" for msg in passed_history)
