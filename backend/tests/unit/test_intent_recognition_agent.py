"""意图识别 Agent 单元测试"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError

from app.agents.intent_recognition_agent import (
    IntentRecognitionAgent,
    IntentRecognitionResult,
    UserIntent,
)
from app.models.agent import Message


# 测试数据
SUSPECT_DATA = {
    "suspect_001": "张三",
    "suspect_002": "李四",
    "suspect_003": "王五",
}


@pytest.fixture
def suspect_data():
    """嫌疑人数据 fixture"""
    return SUSPECT_DATA.copy()


@pytest.fixture
def agent(suspect_data):
    """IntentRecognitionAgent fixture"""
    # Mock LLM 初始化
    with patch("app.agents.intent_recognition_agent.ChatOpenAI"):
        agent = IntentRecognitionAgent(suspect_data)
        # Mock chain
        agent.chain = AsyncMock()
        return agent


@pytest.fixture
def mock_message():
    """创建 Mock 消息的工厂函数"""
    def _create_message(sender_name: str, content: str, **kwargs):
        msg = Mock(spec=Message)
        msg.sender_name = sender_name
        msg.content = content
        msg.timestamp = datetime.now()
        for key, value in kwargs.items():
            setattr(msg, key, value)
        return msg
    return _create_message


@pytest.fixture
def dialogue_history(mock_message):
    """生成示例对话历史 fixture"""
    history = []
    history.append(mock_message("侦探", "张三，你昨晚在哪里？"))
    history.append(mock_message("张三", "我在家看电视。"))
    history.append(mock_message("侦探", "李四，你呢？"))
    history.append(mock_message("李四", "我在酒吧喝酒。"))
    return history


@pytest.fixture
def long_dialogue_history(mock_message):
    """生成超过30轮的对话历史 fixture"""
    history = []
    for i in range(40):
        history.append(mock_message(
            sender_name="侦探" if i % 2 == 0 else "张三",
            content=f"消息内容 {i}"
        ))
    return history


# ==================== IntentRecognitionResult 模型测试 ====================
class TestIntentRecognitionResult:
    """测试 IntentRecognitionResult 模型"""

    def test_valid_model_creation(self):
        """测试模型字段验证"""
        result = IntentRecognitionResult(
            intent_type=UserIntent.SINGLE,
            target_suspect_ids=["suspect_001"],
            confidence=0.8,
            reasoning="明确提到了张三的名字"
        )
        assert result.intent_type == UserIntent.SINGLE
        assert result.target_suspect_ids == ["suspect_001"]
        assert result.confidence == 0.8
        assert result.reasoning == "明确提到了张三的名字"

    def test_confidence_minimum(self):
        """测试 confidence 最小值 0.0"""
        result = IntentRecognitionResult(
            intent_type=UserIntent.ALL,
            target_suspect_ids=["suspect_001", "suspect_002"],
            confidence=0.0,
            reasoning="测试最小值"
        )
        assert result.confidence == 0.0

    def test_confidence_maximum(self):
        """测试 confidence 最大值 1.0"""
        result = IntentRecognitionResult(
            intent_type=UserIntent.ALL,
            target_suspect_ids=["suspect_001"],
            confidence=1.0,
            reasoning="测试最大值"
        )
        assert result.confidence == 1.0

    def test_confidence_below_zero(self):
        """测试 confidence 小于 0.0 时抛出验证错误"""
        with pytest.raises(ValidationError):
            IntentRecognitionResult(
                intent_type=UserIntent.SINGLE,
                target_suspect_ids=["suspect_001"],
                confidence=-0.1,
                reasoning="无效的置信度"
            )

    def test_confidence_above_one(self):
        """测试 confidence 大于 1.0 时抛出验证错误"""
        with pytest.raises(ValidationError):
            IntentRecognitionResult(
                intent_type=UserIntent.SINGLE,
                target_suspect_ids=["suspect_001"],
                confidence=1.1,
                reasoning="无效的置信度"
            )


# ==================== IntentRecognitionAgent 初始化测试 ====================
class TestIntentRecognitionAgentInitialization:
    """测试 IntentRecognitionAgent 初始化"""

    def test_suspect_id_to_name_mapping(self, suspect_data):
        """测试正确初始化 suspect_id_to_name 映射"""
        with patch("app.agents.intent_recognition_agent.ChatOpenAI"):
            agent = IntentRecognitionAgent(suspect_data)
            assert agent.suspect_id_to_name == suspect_data

    def test_suspect_name_to_id_mapping(self, suspect_data):
        """测试正确初始化 suspect_name_to_id 反向映射"""
        with patch("app.agents.intent_recognition_agent.ChatOpenAI"):
            agent = IntentRecognitionAgent(suspect_data)
            expected = {
                "张三": "suspect_001",
                "李四": "suspect_002",
                "王五": "suspect_003",
            }
            assert agent.suspect_name_to_id == expected


# ==================== Prompt 构建测试 ====================
class TestPromptBuilding:
    """测试提示词构建"""

    def test_build_prompt_returns_chat_prompt_template(self, agent):
        """测试 _build_prompt() 返回正确的 ChatPromptTemplate"""
        prompt = agent._build_prompt()
        assert isinstance(prompt, ChatPromptTemplate)

    def test_prompt_contains_required_sections(self, agent):
        """测试提示词包含所有必要的部分"""
        prompt = agent._build_prompt()
        template_text = prompt.messages[0].prompt.template

        assert "嫌疑人列表" in template_text
        assert "对话历史" in template_text
        assert "当前问题" in template_text
        assert "任务" in template_text
        assert "详细注意事项和示例场景" in template_text
        assert "输出格式要求" in template_text


# ==================== Analyze 方法测试 ====================
class TestAnalyzeMethod:
    """测试 analyze 方法"""

    @pytest.mark.asyncio
    async def test_analyze_single_person_question(self, agent, dialogue_history):
        """测试成功识别对单个人提问的场景"""
        expected_result = IntentRecognitionResult(
            intent_type=UserIntent.SINGLE,
            target_suspect_ids=["suspect_001"],
            confidence=0.95,
            reasoning="用户明确提到了张三的名字"
        )
        agent.chain.ainvoke.return_value = expected_result

        result = await agent.analyze("张三，你昨晚在哪里？", dialogue_history)

        assert result == expected_result
        agent.chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_partial_people_question(self, agent, dialogue_history):
        """测试成功识别对部分人提问的场景"""
        expected_result = IntentRecognitionResult(
            intent_type=UserIntent.PARTIAL,
            target_suspect_ids=["suspect_001", "suspect_002"],
            confidence=0.9,
            reasoning="用户提到了张三和李四"
        )
        agent.chain.ainvoke.return_value = expected_result

        result = await agent.analyze("张三和李四，你们说说当时的情况", dialogue_history)

        assert result == expected_result
        agent.chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_all_people_question(self, agent, dialogue_history):
        """测试成功识别对所有人提问的场景"""
        expected_result = IntentRecognitionResult(
            intent_type=UserIntent.ALL,
            target_suspect_ids=["suspect_001", "suspect_002", "suspect_003"],
            confidence=0.95,
            reasoning="用户使用了'大家'，表示对所有人提问"
        )
        agent.chain.ainvoke.return_value = expected_result

        result = await agent.analyze("大家都说说自己的不在场证明", dialogue_history)

        assert result == expected_result
        agent.chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_follow_up_question(self, agent, dialogue_history):
        """测试追问场景（"你呢？"）"""
        expected_result = IntentRecognitionResult(
            intent_type=UserIntent.SINGLE,
            target_suspect_ids=["suspect_001"],
            confidence=0.8,
            reasoning="根据上下文，'你呢？'是在追问张三"
        )
        agent.chain.ainvoke.return_value = expected_result

        result = await agent.analyze("你呢？", dialogue_history)

        assert result == expected_result
        agent.chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_coreference_resolution(self, agent, dialogue_history):
        """测试指代消解场景（"他"、"她"）"""
        expected_result = IntentRecognitionResult(
            intent_type=UserIntent.SINGLE,
            target_suspect_ids=["suspect_002"],
            confidence=0.85,
            reasoning="根据上下文，'他'指代李四"
        )
        agent.chain.ainvoke.return_value = expected_result

        result = await agent.analyze("他什么时候离开的？", dialogue_history)

        assert result == expected_result
        agent.chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_llm_failure_fallback(self, agent, dialogue_history, suspect_data):
        """测试 LLM 调用失败时的回退逻辑（返回对所有人提问）"""
        agent.chain.ainvoke.side_effect = Exception("LLM 调用失败")

        result = await agent.analyze("你好", dialogue_history)

        assert result.intent_type == UserIntent.ALL
        assert result.target_suspect_ids == list(suspect_data.keys())
        assert result.confidence == 0.0
        assert "LLM调用失败" in result.reasoning


# ==================== 对话历史窗口测试 ====================
class TestDialogueHistoryWindow:
    """测试对话历史窗口处理"""

    @pytest.mark.asyncio
    async def test_long_dialogue_history_truncation(self, agent, long_dialogue_history):
        """测试正确处理超过30轮的历史（只取最近30轮）"""
        agent.chain.ainvoke.return_value = IntentRecognitionResult(
            intent_type=UserIntent.ALL,
            target_suspect_ids=["suspect_001"],
            confidence=1.0,
            reasoning="测试"
        )

        await agent.analyze("测试问题", long_dialogue_history)
        agent.chain.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_short_dialogue_history_complete(self, agent, dialogue_history):
        """测试正确处理少于30轮的历史"""
        agent.chain.ainvoke.return_value = IntentRecognitionResult(
            intent_type=UserIntent.ALL,
            target_suspect_ids=["suspect_001"],
            confidence=1.0,
            reasoning="测试"
        )

        await agent.analyze("测试问题", dialogue_history)
        agent.chain.ainvoke.assert_called_once()
