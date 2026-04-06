"""嫌疑人Agent：每个嫌疑人角色独立实例，处理对话逻辑，保证人设一致性"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.core.config import settings
from app.core.constants import SuspectMood, MessageType
from app.models.case import Suspect
from app.models.agent import Message, RolePersona
from app.utils.logger import logger

class SuspectAgent:
    """嫌疑人Agent，每个嫌疑人角色独立实例"""

    def __init__(self, suspect: Suspect, is_murderer: bool = False):
        """
        初始化嫌疑人Agent
        :param suspect: 嫌疑人基本信息
        :param is_murderer: 是否是真凶
        """
        self.suspect_id = suspect.suspect_id
        self.name = suspect.name
        self.age = suspect.age
        self.gender = suspect.gender
        self.occupation = suspect.occupation
        self.relationship_with_victim = suspect.relationship_with_victim
        self.motive = suspect.motive
        self.alibi = suspect.alibi
        self.secrets = suspect.secrets
        self.personality_traits = suspect.personality_traits
        self.is_murderer = is_murderer

        # 状态属性
        self.stress_level: int = 0  # 压力值 0-100，初始0
        self.current_mood: SuspectMood = SuspectMood.CALM
        self.lied_count: int = 0  # 说谎次数

        # LLM配置
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7 + (self.stress_level / 200),  # 压力越高，回答越不稳定
            max_tokens=500,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            # 关闭深度思考模式，加快响应速度
            model_kwargs={
                "reasoning_effort": "none",
                "response_format": {"type": "json_object"}
            }
        )

        # 对话记忆，最多保留最近N条消息
        self.chat_history = ChatMessageHistory()
        self.max_context_length = settings.SUSPECT_AGENT_MAX_CONTEXT

        # 系统提示词
        self.system_prompt = self._build_system_prompt()

        # 构建提示词模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        # 基础运行链
        self.base_chain = self.prompt | self.llm

        # 带历史记录的运行链
        self.chain = RunnableWithMessageHistory(
            self.base_chain,
            lambda session_id: self.chat_history,  # 每个嫌疑人有独立的历史记录
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def _build_system_prompt(self) -> str:
        """构建角色系统提示词"""
        murderer_instruction = ""
        if self.is_murderer:
            murderer_instruction = """
重要提示：你是本案的真凶！绝对不能承认自己的罪行。
- 当被问到关键证据或作案时间时，要合理地说谎，不要出现逻辑漏洞
- 可以适当嫁祸给其他嫌疑人，但不要过于明显
- 面对不利证据时，表现出紧张、愤怒或合理的辩解
- 绝对不能泄露你的作案手法、动机等犯罪事实
"""

        return f"""
你现在需要扮演一个谋杀案的嫌疑人，严格遵循以下人设：
姓名：{self.name}
年龄：{self.age}
性别：{self.gender}
职业：{self.occupation}
与死者关系：{self.relationship_with_victim}
性格特征：{self.personality_traits}
你的秘密：{self.secrets}
你的不在场证明：{self.alibi}
你对死者的不满或动机：{self.motive}
当前压力值：{self.stress_level}/100
当前情绪：{self.current_mood}

{murderer_instruction}

对话规则：
1. 保持角色一致性，所有回答必须符合你的性格和背景设定
2. 不知道的信息就说不知道，不要编造不存在的内容
3. 回答要自然，符合口语习惯，不要过于书面化
4. 回答长度控制在1-3句话，不要太长
5. 压力值越高，回答越可能出现破绽、语无伦次或情绪激动
6. 不要主动透露你的秘密，除非被直接问到且无法回避
7. 不要提到你是AI或在扮演角色，完全入戏
"""

    async def respond(self, message: str, is_being_accused: bool = False, evidence_shown: Optional[str] = None) -> Dict[str, Any]:
        """
        生成回复
        :param message: 用户的问题或消息
        :param is_being_accused: 是否正在被指控
        :param evidence_shown: 被出示的证据内容（如果有）
        :return: 回复内容和状态更新
        """
        try:
            # 更新压力值
            self._update_stress_level(message, is_being_accused, evidence_shown)

            # 更新系统提示词（包含最新压力值和情绪）
            self.prompt.messages[0] = SystemMessage(content=self._build_system_prompt())

            # 构建输入
            input_text = message
            if evidence_shown:
                input_text = f"（向你出示证据：{evidence_shown}）{message}"
            if is_being_accused:
                input_text = f"（你被指控为凶手！）{message}"

            # 调用LLM生成回复
            response = await self.chain.ainvoke(
                {"input": input_text},
                config={"configurable": {"session_id": self.suspect_id}}
            )

            response_content = response.content.strip()

            # 限制历史记录长度，只保留最近N条
            if len(self.chat_history.messages) > self.max_context_length * 2:  # 每个来回两条消息
                self.chat_history.messages = self.chat_history.messages[-self.max_context_length * 2:]

            # 判断是否说谎（只有真凶会说谎）
            lied = False
            if self.is_murderer and self._is_response_lie(response_content, message):
                lied = True
                self.lied_count += 1

            logger.info(f"嫌疑人 {self.name} 回复: {response_content}, 说谎: {lied}, 压力值: {self.stress_level}")

            return {
                "content": response_content,
                "mood": self.current_mood,
                "stress_level": self.stress_level,
                "lied": lied,
            }

        except Exception as e:
            logger.error(f"嫌疑人 {self.name} 生成回复失败: {str(e)}", exc_info=True)
            # 降级处理，返回预设回复
            return {
                "content": "我...我什么都不知道，别问我！",
                "mood": SuspectMood.NERVOUS,
                "stress_level": self.stress_level,
                "lied": False,
            }

    def _update_stress_level(self, message: str, is_being_accused: bool, evidence_shown: Optional[str]) -> None:
        """更新压力值和情绪"""
        stress_increase = 0

        # 被指控时压力大幅上升
        if is_being_accused:
            stress_increase += 30

        # 被出示不利证据时压力大幅上升
        if evidence_shown:
            stress_increase += 25

        # 问题涉及关键信息时压力上升
        key_words = ["作案时间", "当时你在哪", "凶器", "动机", "你和死者的关系", "你有没有", "是不是你"]
        for word in key_words:
            if word in message:
                stress_increase += 10
                break

        # 真凶压力上升更快
        if self.is_murderer:
            stress_increase = int(stress_increase * 1.5)

        # 更新压力值（0-100）
        self.stress_level = min(100, self.stress_level + stress_increase)

        # 随着时间推移压力缓慢下降
        self.stress_level = max(0, self.stress_level - 5)

        # 更新情绪状态
        if self.stress_level < 20:
            self.current_mood = SuspectMood.CALM
        elif self.stress_level < 40:
            self.current_mood = SuspectMood.NERVOUS
        elif self.stress_level < 60:
            self.current_mood = SuspectMood.ANGRY
        elif self.stress_level < 80:
            self.current_mood = SuspectMood.SCARED
        else:
            self.current_mood = SuspectMood.GUILTY

    def _is_response_lie(self, response: str, question: str) -> bool:
        """简单判断回答是否是谎言（仅适用于真凶）"""
        # 这里可以实现更复杂的谎言检测逻辑，v1.0用简单规则
        lie_indicators = ["我没有", "不是我", "我不知道", "我当时在", "你胡说"]
        for indicator in lie_indicators:
            if indicator in response and self.is_murderer:
                return True
        return False

    def add_history_message(self, message: Message) -> None:
        """添加历史消息到记忆中"""
        if message.role == "user":
            self.chat_history.add_message(HumanMessage(content=message.content))
        elif message.role == "suspect" and message.sender_id == self.suspect_id:
            self.chat_history.add_message(AIMessage(content=message.content))

        # 限制历史记录长度
        if len(self.chat_history.messages) > self.max_context_length * 2:
            self.chat_history.messages = self.chat_history.messages[-self.max_context_length * 2:]

    def clear_memory(self) -> None:
        """清空对话记忆"""
        self.chat_history.clear()
        self.stress_level = 0
        self.current_mood = SuspectMood.CALM
        self.lied_count = 0
