"""
反驳决策引擎 - 评估威胁程度，决定是否进行反驳
"""
from enum import Enum
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field

from app.models.case import Suspect, ContradictionPoint
from app.core.constants import ContradictionType
from app.models.agent import Message
from app.utils.logger import logger


class ThreatLevel(float, Enum):
    """威胁程度等级"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.85
    CRITICAL = 0.95


class RefusalDecisionEngine:
    """反驳决策引擎"""

    def __init__(self, suspects: List[Suspect]):
        self.suspects = {s.suspect_id: s for s in suspects}
        self.max_refusals_per_round = 2

    async def make_refusal_decision(
        self,
        contradiction: Dict[str, Any],
        current_refusal_count: int,
        dialogue_history: List[Message]
    ) -> Tuple[bool, Optional[str]]:
        """
        做出是否反驳的决策
        :param contradiction: 矛盾点信息
        :param current_refusal_count: 当前轮次已反驳次数
        :param dialogue_history: 对话历史
        :return: (是否反驳, 反驳理由提示词)
        """
        # 1. 检查反驳次数限制
        if current_refusal_count >= self.max_refusals_per_round:
            logger.debug(f"反驳次数已达上限（{self.max_refusals_per_round}次），不再进行反驳")
            return False, None

        target_suspect_id = contradiction["target_suspect"]
        refuting_suspect_id = contradiction["refuting_suspect"]
        contradiction_point = contradiction["contradiction"]

        # 2. 获取嫌疑人信息
        target_suspect = self.suspects.get(target_suspect_id)
        refuting_suspect = self.suspects.get(refuting_suspect_id)

        if not target_suspect or not refuting_suspect:
            logger.warning(f"找不到嫌疑人信息 - 目标: {target_suspect_id}, 反驳者: {refuting_suspect_id}")
            return False, None

        # 3. 评估威胁程度
        threat_score = self._assess_threat_level(
            contradiction_point,
            refuting_suspect
        )

        # 4. 检查反驳证据
        evidence_score = self._check_counter_evidence(
            contradiction_point,
            refuting_suspect
        )

        # 5. 考虑人设因素
        personality_modifier = refuting_suspect.personality_modifier

        # 6. 计算最终得分
        final_score = threat_score * evidence_score * personality_modifier

        # 7. 与阈值比较
        threshold = refuting_suspect.refusal_threshold

        logger.info(
            f"反驳决策 - 嫌疑人: {refuting_suspect.name}, "
            f"威胁分: {threat_score:.2f}, 证据分: {evidence_score:.2f}, "
            f"人设修正: {personality_modifier:.2f}, 最终分: {final_score:.2f}, 阈值: {threshold:.2f}"
        )

        if final_score >= threshold:
            # 生成反驳提示词
            refusal_prompt = self._generate_refusal_prompt(
                contradiction_point,
                target_suspect,
                refuting_suspect
            )
            return True, refusal_prompt

        logger.debug(
            f"反驳得分未达到阈值 - 最终分: {final_score:.2f}, 阈值: {threshold:.2f}"
        )
        return False, None

    def _assess_threat_level(
        self,
        contradiction: ContradictionPoint,
        refuting_suspect: Suspect
    ) -> float:
        """
        评估威胁程度（0-1）
        """
        # 根据矛盾类型评估
        if contradiction.type == ContradictionType.EVIDENCE:
            # 被出示关键证据 - 高威胁
            return ThreatLevel.CRITICAL

        elif contradiction.type == ContradictionType.TIMELINE:
            # 时间线被质疑 - 中高威胁
            return ThreatLevel.HIGH

        elif contradiction.type == ContradictionType.SPATIAL:
            # 空间关系矛盾 - 中等威胁
            return ThreatLevel.MEDIUM

        # 默认中等威胁
        return ThreatLevel.MEDIUM

    def _check_counter_evidence(
        self,
        contradiction: ContradictionPoint,
        refuting_suspect: Suspect
    ) -> float:
        """
        检查反驳证据充分度（0-1）
        """
        # 检查counter_evidence中是否有相关证据
        contradiction_key = contradiction.description[:20]  # 取前20字作为key

        for key, evidence in refuting_suspect.counter_evidence.items():
            if key in contradiction.description or contradiction_key in key:
                # 有确凿证据
                return 1.0

        # 检查是否有相关线索
        # (简化实现，实际可以更复杂)
        return 0.6  # 默认有一定理由可以反驳

    def _generate_refusal_prompt(
        self,
        contradiction: ContradictionPoint,
        target_suspect: Suspect,
        refuting_suspect: Suspect
    ) -> str:
        """生成反驳提示词"""
        return f"""
你是{refuting_suspect.name}，你听到{target_suspect.name}的话，发现了矛盾。

请根据你的人设，进行插话反驳：
- 保持你的性格特点：{', '.join(refuting_suspect.personality_traits)}
- 反驳要自然，符合对话场景
- 可以指出对方的矛盾，但不要太咄咄逼人
- 反驳内容控制在1-2句话

矛盾点：{contradiction.description}
你可以使用的反驳理由：{refuting_suspect.counter_evidence}
"""
