"""对话管理器：控制对话流程、发言优先级、频率，保证游戏体验"""
import random
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from app.core.config import settings
from app.core.constants import MessagePriority, DialogueMode, SuspectMood
from app.models.agent import Message
from app.models.case import Suspect, Case
from app.agents.suspect_agent import SuspectAgent
from app.agents.contradiction_detector import ContradictionDetector
from app.agents.refusal_decision_engine import RefusalDecisionEngine
from app.utils.logger import logger


class UserIntent(str, Enum):
    """用户提问意图类型"""
    SINGLE = "single"  # 对一个人提问
    PARTIAL = "partial"  # 对部分人提问
    ALL = "all"  # 对所有人提问


class DialogueManager:
    """对话管理器，控制发言顺序、优先级和频率"""

    def __init__(self, suspects: List[Suspect], true_murderer_id: str, case: Optional[Case] = None):
        """
        初始化对话管理器
        :param suspects: 嫌疑人列表
        :param true_murderer_id: 真凶ID
        :param case: 完整案件数据（用于矛盾检测）
        """
        self.suspect_agents: Dict[str, SuspectAgent] = {}
        for suspect in suspects:
            is_murderer = suspect.suspect_id == true_murderer_id
            self.suspect_agents[suspect.suspect_id] = SuspectAgent(suspect, is_murderer)

        self.dialogue_mode: DialogueMode = DialogueMode.GROUP
        self.current_interrogation_suspect: Optional[str] = None  # 单独审讯的嫌疑人ID
        self.last_speaker_times: Dict[str, datetime] = {}  # 每个嫌疑人最后发言时间
        self.active_speakers: List[str] = []  # 当前轮次需要发言的嫌疑人列表
        self.current_speaker_index: int = 0

        # 发言频率控制参数
        self.min_speech_interval: timedelta = timedelta(seconds=10)  # 最小发言间隔
        self.max_active_speakers_per_round: int = 3  # 每轮最多发言人数

        # 存储嫌疑人信息，用于意图识别
        self.suspect_names: Dict[str, str] = {
            suspect.suspect_id: suspect.name
            for suspect in suspects
        }
        self.name_to_id: Dict[str, str] = {
            suspect.name: suspect.suspect_id
            for suspect in suspects
        }

        # 新增：矛盾检测和反驳机制
        self.contradiction_detector: Optional[ContradictionDetector] = None
        self.refusal_decision_engine: Optional[RefusalDecisionEngine] = None
        if case:
            self.contradiction_detector = ContradictionDetector(case)
            self.refusal_decision_engine = RefusalDecisionEngine(suspects)

        # 新增：反驳计数管理
        self.refusal_count: int = 0
        self.last_refusal_reset: datetime = datetime.utcnow()
        self.max_refusals_per_round: int = 2

    async def process_user_message(
        self,
        message: str,
        target_suspects: Optional[List[str]] = None,
        is_accusation: bool = False,
        evidence_shown: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        处理用户发送的消息，生成嫌疑人回复（增强版：包含矛盾检测和反驳机制）
        :param message: 用户消息内容
        :param target_suspects: @的嫌疑人ID列表
        :param is_accusation: 是否是指控
        :param evidence_shown: 出示的证据内容
        :return: (嫌疑人回复列表, 系统提示列表)
        """
        logger.info(f"处理用户消息: {message}, 目标嫌疑人: {target_suspects}")

        # 1. 重置反驳计数（每轮用户消息开始时）
        self._reset_refusal_count()

        # 2. 确定需要回复的嫌疑人优先级
        priority_queue = self._determine_reply_priority(message, target_suspects, is_accusation)

        responses = []
        system_prompts = []

        # 3. 生成嫌疑人回复
        for suspect_id, priority in priority_queue:
            # 检查发言间隔限制
            if not self._can_speak_now(suspect_id):
                continue

            # 调用嫌疑人Agent生成回复
            agent = self.suspect_agents[suspect_id]
            response = await agent.respond(
                message=message,
                is_being_accused=is_accusation and suspect_id in (target_suspects or []),
                evidence_shown=evidence_shown if suspect_id in (target_suspects or []) else None,
            )

            # 记录发言时间
            self.last_speaker_times[suspect_id] = datetime.now()

            responses.append({
                "suspect_id": suspect_id,
                "name": agent.name,
                "content": response["content"],
                "mood": response["mood"],
                "stress_level": response["stress_level"],
                "lied": response["lied"],
                "priority": priority,
            })

            # 限制每轮回复人数
            if len(responses) >= self._get_max_responses():
                break

        # 4. 新增：矛盾检测
        refutable_contradictions = []
        if self.contradiction_detector:
            system_hints_from_detector, refutable_contradictions = await self.contradiction_detector.analyze_dialogue(
                self._get_dialogue_history(),
                responses
            )
            system_prompts.extend(system_hints_from_detector)

        # 5. 新增：处理反驳
        refusal_responses = []
        if self.refusal_decision_engine and refutable_contradictions:
            for contradiction_info in refutable_contradictions:
                # 检查是否应该反驳
                should_refuse, refusal_prompt = await self.refusal_decision_engine.make_refusal_decision(
                    contradiction_info,
                    self.refusal_count,
                    self._get_dialogue_history()
                )

                if should_refuse and refusal_prompt:
                    # 生成反驳回复
                    refuting_suspect_id = contradiction_info["refuting_suspect"]
                    agent = self.suspect_agents.get(refuting_suspect_id)

                    if agent:
                        refusal_response = await agent.respond_with_prompt(
                            refusal_prompt,
                            message_type="refusal"
                        )
                        refusal_response["suspect_id"] = refuting_suspect_id
                        refusal_response["name"] = agent.name
                        refusal_response["is_refusal"] = True
                        refusal_responses.append(refusal_response)

                        # 增加反驳计数
                        self.refusal_count += 1

                        # 达到上限停止
                        if self.refusal_count >= self.max_refusals_per_round:
                            break

        # 6. 合并回复
        all_responses = responses + refusal_responses

        # 7. 原有矛盾检测（保留作为补充）
        contradictions = self._detect_contradictions(all_responses)
        system_prompts.extend(contradictions)

        # 8. 压力值过高提示
        for resp in all_responses:
            if resp.get("stress_level", 0) >= 80:
                system_prompts.append(f"⚠️ {resp.get('name', '嫌疑人')} 情绪非常激动，看起来有很大压力！")
            elif resp.get("stress_level", 0) >= 60 and resp.get("mood") == SuspectMood.GUILTY:
                system_prompts.append(f"🤨 {resp.get('name', '嫌疑人')} 看起来有些心虚，回答很可疑。")

        logger.info(f"生成 {len(all_responses)} 条嫌疑人回复（含{len(refusal_responses)}条反驳），系统提示 {len(system_prompts)} 条")
        return all_responses, system_prompts

    def _analyze_user_intent(self, message: str) -> Tuple[UserIntent, List[str]]:
        """
        分析用户提问意图
        :param message: 用户消息
        :return: (意图类型, 目标嫌疑人ID列表)
        """
        message_lower = message.lower()

        # 1. 检查是否有对所有人提问的关键词
        all_keywords = ["大家", "所有人", "各位", "都", "你们全部", "每个", "统统"]
        if any(keyword in message for keyword in all_keywords):
            logger.info(f"识别为对所有人提问: {message}")
            return UserIntent.ALL, list(self.suspect_agents.keys())

        # 2. 检查消息中提到的嫌疑人名字
        mentioned_suspects = []
        for name, suspect_id in self.name_to_id.items():
            # 检查名字是否在消息中（作为完整词）
            if name in message:
                mentioned_suspects.append(suspect_id)

        if mentioned_suspects:
            if len(mentioned_suspects) == 1:
                logger.info(f"识别为对一个人提问: {message}, 嫌疑人: {mentioned_suspects}")
                return UserIntent.SINGLE, mentioned_suspects
            else:
                logger.info(f"识别为对部分人提问: {message}, 嫌疑人: {mentioned_suspects}")
                return UserIntent.PARTIAL, mentioned_suspects

        # 3. 默认：如果没有明确指向，认为是对所有人提问
        logger.info(f"未明确指向，默认为对所有人提问: {message}")
        return UserIntent.ALL, list(self.suspect_agents.keys())

    def _determine_reply_priority(
        self,
        message: str,
        target_suspects: Optional[List[str]],
        is_accusation: bool,
    ) -> List[Tuple[str, int]]:
        """确定嫌疑人回复优先级"""
        priority_list = []

        # 如果是单独审讯模式，只有被审讯的嫌疑人回复
        if self.dialogue_mode == DialogueMode.SINGLE and self.current_interrogation_suspect:
            return [(self.current_interrogation_suspect, MessagePriority.P0)]

        # 分析用户意图
        intent, intent_targets = self._analyze_user_intent(message)

        # 根据意图确定优先级
        if intent == UserIntent.SINGLE:
            # 对一个人提问：只有被提问的人回复
            for suspect_id in intent_targets:
                if suspect_id in self.suspect_agents:
                    priority_list.append((suspect_id, MessagePriority.P0))

        elif intent == UserIntent.PARTIAL:
            # 对部分人提问：被提问的人优先回复
            for suspect_id in intent_targets:
                if suspect_id in self.suspect_agents:
                    priority_list.append((suspect_id, MessagePriority.P0))

        elif intent == UserIntent.ALL:
            # 对所有人提问：所有人都可以回复，不限制人数
            # P0优先级：用户直接@的嫌疑人或被指控的嫌疑人
            if target_suspects:
                for suspect_id in target_suspects:
                    if suspect_id in self.suspect_agents:
                        priority_list.append((suspect_id, MessagePriority.P0))

            # P1优先级：与问题内容相关的嫌疑人
            for suspect_id, agent in self.suspect_agents.items():
                if suspect_id not in [x[0] for x in priority_list]:
                    # 简单关键词匹配判断相关性
                    if agent.name in message or any(keyword in message for keyword in [agent.occupation, agent.relationship_with_victim]):
                        priority_list.append((suspect_id, MessagePriority.P1))

            # P2优先级：其他所有人
            for suspect_id in self.suspect_agents.keys():
                if suspect_id not in [x[0] for x in priority_list]:
                    priority_list.append((suspect_id, MessagePriority.P2))

            # 按优先级排序
            priority_list.sort(key=lambda x: x[1])
            return priority_list

        # P0优先级：用户直接@的嫌疑人或被指控的嫌疑人（补充）
        if target_suspects:
            for suspect_id in target_suspects:
                if suspect_id in self.suspect_agents and suspect_id not in [x[0] for x in priority_list]:
                    priority_list.append((suspect_id, MessagePriority.P0))

        # P1优先级：与问题内容相关的嫌疑人（补充）
        for suspect_id, agent in self.suspect_agents.items():
            if suspect_id not in [x[0] for x in priority_list]:
                # 简单关键词匹配判断相关性
                if agent.name in message or any(keyword in message for keyword in [agent.occupation, agent.relationship_with_victim]):
                    priority_list.append((suspect_id, MessagePriority.P1))

        # P2优先级：随机主动发言
        if len(priority_list) == 0 or random.random() < 0.2:  # 20%概率有其他嫌疑人主动发言
            all_suspects = list(self.suspect_agents.keys())
            random.shuffle(all_suspects)
            num_speakers = random.randint(1, 2)  # 至少1个，最多2个主动发言
            for suspect_id in all_suspects[:num_speakers]:
                if suspect_id not in [x[0] for x in priority_list]:
                    priority_list.append((suspect_id, MessagePriority.P2))

        # 确保至少有一个嫌疑人回复（防止优先级队列为空）
        if len(priority_list) == 0:
            all_suspects = list(self.suspect_agents.keys())
            random.shuffle(all_suspects)
            # 全体模式下返回1-3个嫌疑人，单独模式下返回被审讯的嫌疑人
            num_speakers = min(self._get_max_responses(), len(all_suspects))
            for suspect_id in all_suspects[:num_speakers]:
                priority_list.append((suspect_id, MessagePriority.P2))

        # 按优先级排序
        priority_list.sort(key=lambda x: x[1])
        return priority_list

    def _can_speak_now(self, suspect_id: str) -> bool:
        """检查嫌疑人是否可以发言（冷却时间限制）"""
        last_time = self.last_speaker_times.get(suspect_id)
        if not last_time:
            return True
        return datetime.now() - last_time >= self.min_speech_interval

    def _get_max_responses(self) -> int:
        """获取当前轮次最大回复人数"""
        if self.dialogue_mode == DialogueMode.SINGLE:
            return 1
        # 全体模式下，如果是对所有人提问，允许所有人回复
        return len(self.suspect_agents)

    def _detect_contradictions(self, responses: List[Dict[str, Any]]) -> List[str]:
        """检测回复中的矛盾点，生成系统提示"""
        # v1.0实现简单的矛盾检测逻辑
        contradictions = []

        # 检测是否有明显的说谎
        liars = [resp for resp in responses if resp.get("lied", False)]
        if liars:
            for liar in liars:
                if random.random() < 0.3:  # 30%概率提示矛盾
                    contradictions.append(f"❓ {liar['name']} 的回答听起来有些不对劲，可能在撒谎。")

        # 检测情绪冲突
        angry_responses = [resp for resp in responses if resp["mood"] == SuspectMood.ANGRY]
        if len(angry_responses) >= 2:
            contradictions.append("🔥 现场气氛很紧张，嫌疑人之间似乎有矛盾。")

        return contradictions

    def switch_interrogation_mode(self, mode: DialogueMode, suspect_id: Optional[str] = None) -> Dict[str, Any]:
        """切换审讯模式"""
        self.dialogue_mode = mode

        if mode == DialogueMode.SINGLE:
            # 单独审讯模式需要嫌疑人ID
            if not suspect_id:
                # 如果没有提供嫌疑人ID，使用第一个嫌疑人
                suspect_id = next(iter(self.suspect_agents.keys()))

            if suspect_id in self.suspect_agents:
                self.current_interrogation_suspect = suspect_id
                suspect_name = self.suspect_agents[suspect_id].name
                logger.info(f"切换到单独审讯模式，审讯对象: {suspect_name}")
                return {
                    "mode": mode,
                    "suspect_id": suspect_id,
                    "suspect_name": suspect_name,
                    "message": f"已切换到单独审讯模式，现在可以单独审讯 {suspect_name}",
                }
            else:
                raise ValueError(f"无效的嫌疑人ID: {suspect_id}")
        else:
            # 全体质询模式不需要嫌疑人ID
            self.current_interrogation_suspect = None
            logger.info("切换到全体质询模式")
            return {
                "mode": mode,
                "suspect_id": None,
                "suspect_name": None,
                "message": "已切换到全体质询模式，所有嫌疑人都可以发言",
            }

    def add_history_message(self, message: Message) -> None:
        """添加历史消息到所有嫌疑人的记忆中"""
        for agent in self.suspect_agents.values():
            agent.add_history_message(message)

    def get_suspect_state(self, suspect_id: Optional[str] = None) -> Any:
        """获取嫌疑人状态"""
        if suspect_id:
            agent = self.suspect_agents.get(suspect_id)
            if not agent:
                return None
            return {
                "suspect_id": agent.suspect_id,
                "name": agent.name,
                "stress_level": agent.stress_level,
                "mood": agent.current_mood,
                "lied_count": agent.lied_count,
                "is_murderer": agent.is_murderer,
            }
        else:
            return [
                {
                    "suspect_id": agent.suspect_id,
                    "name": agent.name,
                    "stress_level": agent.stress_level,
                    "mood": agent.current_mood,
                    "lied_count": agent.lied_count,
                }
                for agent in self.suspect_agents.values()
            ]

    def _reset_refusal_count(self):
        """重置反驳计数"""
        now = datetime.utcnow()
        # 每2分钟或新用户消息重置
        if (now - self.last_refusal_reset) > timedelta(minutes=2):
            self.refusal_count = 0
            self.last_refusal_reset = now
        else:
            # 每轮新用户消息也重置
            self.refusal_count = 0
            self.last_refusal_reset = now

    def _get_dialogue_history(self) -> List[Message]:
        """获取对话历史（从session_service获取，v1.0返回空列表）"""
        # 简化实现，实际从session获取
        return []

    def reset(self) -> None:
        """重置对话管理器状态"""
        for agent in self.suspect_agents.values():
            agent.clear_memory()
        self.last_speaker_times.clear()
        self.active_speakers.clear()
        self.current_speaker_index = 0
        self.dialogue_mode = DialogueMode.GROUP
        self.current_interrogation_suspect = None
        self.refusal_count = 0
        self.last_refusal_reset = datetime.utcnow()
