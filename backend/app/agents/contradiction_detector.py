"""
矛盾检测引擎
负责分析对话历史，识别潜在矛盾点，生成系统提示
"""
from typing import List, Optional, Dict, Any, Tuple
from app.models.case import Case, ContradictionPoint, Clue
from app.core.constants import ContradictionType, ClueType, ClueStatus
from app.models.agent import Message
from app.utils.logger import logger


class ContradictionDetector:
    """矛盾检测引擎"""

    def __init__(self, case: Case):
        """
        初始化矛盾检测引擎
        :param case: 完整案件数据
        """
        self.case = case
        self.contradiction_points: List[ContradictionPoint] = case.contradiction_points
        logger.info(f"矛盾检测引擎初始化完成，共加载 {len(self.contradiction_points)} 个矛盾点")

    async def analyze_dialogue(
        self, dialogue_history: List[Message], latest_responses: List[Message]
    ) -> Tuple[List[str], List[ContradictionPoint]]:
        """
        分析对话历史，识别矛盾点
        :param dialogue_history: 完整对话历史
        :param latest_responses: 最新回复消息列表
        :return: (系统提示列表, 可触发反驳的矛盾点列表)
        """
        logger.debug("开始分析对话历史，查找矛盾点")
        system_hints: List[str] = []
        refutable_contradictions: List[ContradictionPoint] = []

        for contradiction in self.contradiction_points:
            logger.debug(f"检查矛盾点: {contradiction.contradiction_id} - {contradiction.description}")

            # 检查是否满足触发条件
            if await self._check_trigger_condition(contradiction, dialogue_history, latest_responses):
                logger.info(f"矛盾点满足触发条件: {contradiction.contradiction_id}")

                # 生成系统提示
                if contradiction.hint_for_user:
                    system_hints.append(contradiction.hint_for_user)

                # 检查是否可以触发反驳
                if self._can_trigger_refusal(contradiction):
                    logger.debug(f"矛盾点可触发反驳: {contradiction.contradiction_id}")
                    refutable_contradictions.append(contradiction)

        logger.debug(f"对话分析完成，找到 {len(system_hints)} 个系统提示，{len(refutable_contradictions)} 个可反驳矛盾点")
        return system_hints, refutable_contradictions

    async def _check_trigger_condition(
        self, contradiction: ContradictionPoint, dialogue_history: List[Message], latest_responses: List[Message]
    ) -> bool:
        """
        检查矛盾点触发条件
        :param contradiction: 矛盾点
        :param dialogue_history: 完整对话历史
        :param latest_responses: 最新回复
        :return: 是否满足触发条件
        """
        # 检查是否需要所有涉及的嫌疑人都发言了
        if contradiction.trigger_condition.get("requires_both_speaking", True):
            all_spoke = await self._check_all_involved_suspects_spoke(contradiction, dialogue_history)
            if not all_spoke:
                logger.debug(f"矛盾点 {contradiction.contradiction_id} 未满足所有嫌疑人发言条件")
                return False

        # 检查关键词匹配
        if "keywords" in contradiction.trigger_condition:
            keywords = contradiction.trigger_condition["keywords"]
            if not await self._check_keyword_match(contradiction, keywords, dialogue_history, latest_responses):
                logger.debug(f"矛盾点 {contradiction.contradiction_id} 未匹配到关键词: {keywords}")
                return False

        return True

    async def _check_all_involved_suspects_spoke(
        self, contradiction: ContradictionPoint, dialogue_history: List[Message]
    ) -> bool:
        """
        检查所有涉及的嫌疑人是否都发言了
        :param contradiction: 矛盾点
        :param dialogue_history: 对话历史
        :return: 是否所有涉及的嫌疑人都发言了
        """
        spoke_suspects = set()

        for msg in dialogue_history:
            if msg.role == "suspect" and msg.sender_id in contradiction.involved_suspects:
                spoke_suspects.add(msg.sender_id)

        logger.debug(f"涉及的嫌疑人: {contradiction.involved_suspects}, 已发言: {list(spoke_suspects)}")
        return len(spoke_suspects) == len(contradiction.involved_suspects)

    async def _check_keyword_match(
        self, contradiction: ContradictionPoint, keywords: List[str], dialogue_history: List[Message],
        latest_responses: List[Message]
    ) -> bool:
        """
        检查关键词匹配
        :param contradiction: 矛盾点
        :param keywords: 关键词列表
        :param dialogue_history: 对话历史
        :param latest_responses: 最新回复
        :return: 是否匹配到关键词
        """
        # 检查最新回复中是否包含关键词
        for msg in latest_responses:
            if msg.role == "suspect" and msg.sender_id in contradiction.involved_suspects:
                for keyword in keywords:
                    if keyword in msg.content:
                        logger.debug(f"在消息 {msg.message_id} 中找到关键词: {keyword}")
                        return True

        # 如果最新回复中没有找到，检查整个对话历史
        for msg in dialogue_history:
            if msg.role == "suspect" and msg.sender_id in contradiction.involved_suspects:
                for keyword in keywords:
                    if keyword in msg.content:
                        logger.debug(f"在对话历史 {msg.message_id} 中找到关键词: {keyword}")
                        return True

        return False

    def _can_trigger_refusal(self, contradiction: ContradictionPoint) -> bool:
        """
        检查是否可以触发反驳
        :param contradiction: 矛盾点
        :return: 是否可以触发反驳
        """
        # 只有特定类型的矛盾才触发反驳
        if contradiction.contradiction_type in [
            ContradictionType.TIMELINE,
            ContradictionType.EVIDENCE
        ]:
            return True
        return False

    def _get_refusal_target(self, contradiction: ContradictionPoint) -> Optional[str]:
        """
        获取被反驳目标
        :param contradiction: 矛盾点
        :return: 被反驳目标的嫌疑人ID
        """
        if hasattr(contradiction, "refutation_target") and contradiction.refutation_target:
            return contradiction.refutation_target

        # 默认返回第一个涉及的嫌疑人
        if contradiction.involved_suspects:
            return contradiction.involved_suspects[0]

        return None

    def _get_refuting_suspect(self, contradiction: ContradictionPoint) -> Optional[str]:
        """
        获取反驳者
        :param contradiction: 矛盾点
        :return: 反驳者的嫌疑人ID
        """
        if hasattr(contradiction, "refuting_suspect") and contradiction.refuting_suspect:
            return contradiction.refuting_suspect

        # 默认返回第二个涉及的嫌疑人
        if len(contradiction.involved_suspects) > 1:
            return contradiction.involved_suspects[1]

        return None

    def generate_contradiction_clue(self, contradiction: ContradictionPoint) -> Optional[Clue]:
        """
        生成矛盾线索
        :param contradiction: 矛盾点
        :return: 生成的线索对象，或None（如果没有关联线索）
        """
        if not hasattr(contradiction, "related_clue_id") or not contradiction.related_clue_id:
            logger.debug(f"矛盾点 {contradiction.contradiction_id} 没有关联线索")
            return None

        # 检查是否已经存在该线索
        existing_clue = next((c for c in self.case.clues if c.clue_id == contradiction.related_clue_id), None)
        if existing_clue:
            logger.debug(f"线索 {contradiction.related_clue_id} 已存在，无需生成")
            return existing_clue

        # 生成新线索
        clue = Clue(
            clue_id=contradiction.related_clue_id,
            name=f"矛盾点线索: {contradiction.description[:20]}...",
            clue_type=ClueType.TESTIMONY,
            status=ClueStatus.HIDDEN,
            description=f"与矛盾点相关的线索: {contradiction.description}",
            location=getattr(contradiction, "clue_location", "未知位置"),
            scene="unknown",
            content=f"该线索揭示了以下矛盾: {contradiction.description}",
            related_suspects=contradiction.involved_suspects,
            importance=0.8,
            is_red_herring=False
        )

        logger.info(f"为矛盾点 {contradiction.contradiction_id} 生成新线索: {clue.clue_id}")
        return clue
