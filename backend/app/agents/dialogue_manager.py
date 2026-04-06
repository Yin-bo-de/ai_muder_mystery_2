"""对话管理器：控制对话流程、发言优先级、频率，保证游戏体验"""
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.constants import MessagePriority, DialogueMode, SuspectMood
from app.models.agent import Message
from app.models.case import Suspect
from app.agents.suspect_agent import SuspectAgent
from app.utils.logger import logger

class DialogueManager:
    """对话管理器，控制发言顺序、优先级和频率"""

    def __init__(self, suspects: List[Suspect], true_murderer_id: str):
        """
        初始化对话管理器
        :param suspects: 嫌疑人列表
        :param true_murderer_id: 真凶ID
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

    async def process_user_message(
        self,
        message: str,
        target_suspects: Optional[List[str]] = None,
        is_accusation: bool = False,
        evidence_shown: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        处理用户发送的消息，生成嫌疑人回复
        :param message: 用户消息内容
        :param target_suspects: @的嫌疑人ID列表
        :param is_accusation: 是否是指控
        :param evidence_shown: 出示的证据内容
        :return: (嫌疑人回复列表, 系统提示列表)
        """
        logger.info(f"处理用户消息: {message}, 目标嫌疑人: {target_suspects}")

        # 确定需要回复的嫌疑人优先级
        priority_queue = self._determine_reply_priority(message, target_suspects, is_accusation)

        responses = []
        system_prompts = []

        # 生成回复
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

        # 检测矛盾点，生成系统提示
        contradictions = self._detect_contradictions(responses)
        system_prompts.extend(contradictions)

        # 压力值过高提示
        for resp in responses:
            if resp["stress_level"] >= 80:
                system_prompts.append(f"⚠️ {resp['name']} 情绪非常激动，看起来有很大压力！")
            elif resp["stress_level"] >= 60 and resp["mood"] == SuspectMood.GUILTY:
                system_prompts.append(f"🤨 {resp['name']} 看起来有些心虚，回答很可疑。")

        logger.info(f"生成 {len(responses)} 条嫌疑人回复，系统提示 {len(system_prompts)} 条")
        return responses, system_prompts

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

        # P2优先级：随机主动发言（低概率）
        if len(priority_list) == 0 or random.random() < 0.2:  # 20%概率有其他嫌疑人主动发言
            all_suspects = list(self.suspect_agents.keys())
            random.shuffle(all_suspects)
            for suspect_id in all_suspects[:random.randint(0, 2)]:  # 最多2个主动发言
                if suspect_id not in [x[0] for x in priority_list]:
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
        return min(self.max_active_speakers_per_round, len(self.suspect_agents))

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
            if not suspect_id or suspect_id not in self.suspect_agents:
                raise ValueError(f"无效的嫌疑人ID: {suspect_id}")
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

    def reset(self) -> None:
        """重置对话管理器状态"""
        for agent in self.suspect_agents.values():
            agent.clear_memory()
        self.last_speaker_times.clear()
        self.active_speakers.clear()
        self.current_speaker_index = 0
        self.dialogue_mode = DialogueMode.GROUP
        self.current_interrogation_suspect = None
