"""线索服务：线索管理、关联、解密逻辑"""
from typing import List, Dict, Any, Optional
from collections import defaultdict

from app.core.constants import ClueStatus, ClueType
from app.core.exceptions import SessionNotFoundException, ClueNotFoundException
from app.models.case import Clue
from .session_service import session_service
from app.utils.logger import logger

class ClueService:
    """线索管理服务"""

    @staticmethod
    def get_collected_clues(session_id: str, clue_type: Optional[ClueType] = None) -> List[Clue]:
        """
        获取用户已收集的线索列表
        :param session_id: 会话ID
        :param clue_type: 线索类型过滤（可选）
        :return: 线索列表
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        clues = session.collected_clues

        if clue_type:
            clues = [clue for clue in clues if clue.clue_type == clue_type]

        return clues

    @staticmethod
    def get_clue_detail(session_id: str, clue_id: str) -> Clue:
        """
        获取线索详细信息
        :param session_id: 会话ID
        :param clue_id: 线索ID
        :return: 线索详情
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        clue = next((c for c in session.collected_clues if c.clue_id == clue_id), None)
        if not clue:
            raise ClueNotFoundException()

        return clue

    @staticmethod
    def get_clues_by_scene(session_id: str, scene: str) -> List[Clue]:
        """
        获取指定场景的已收集线索
        :param session_id: 会话ID
        :param scene: 场景名称
        :return: 线索列表
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        return [clue for clue in session.collected_clues if clue.scene == scene]

    @staticmethod
    def get_clue_statistics(session_id: str) -> Dict[str, Any]:
        """
        获取线索统计信息
        :param session_id: 会话ID
        :return: 统计信息
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        total_clues = len(session.case.clues)
        collected_clues = len(session.collected_clues)

        # 按类型统计
        type_stats = defaultdict(int)
        for clue in session.collected_clues:
            type_stats[clue.clue_type] += 1

        # 按状态统计
        status_stats = defaultdict(int)
        for clue in session.collected_clues:
            status_stats[clue.status] += 1

        # 按场景统计
        scene_stats = defaultdict(int)
        for clue in session.collected_clues:
            scene_stats[clue.scene] += 1

        return {
            "total_clues": total_clues,
            "collected_clues": collected_clues,
            "completion_rate": round((collected_clues / total_clues) * 100) if total_clues > 0 else 0,
            "type_statistics": dict(type_stats),
            "status_statistics": dict(status_stats),
            "scene_statistics": dict(scene_stats),
            "undiscovered_clues_count": total_clues - collected_clues,
        }

    @staticmethod
    def get_related_clues(session_id: str, clue_id: str) -> List[Clue]:
        """
        获取与指定线索相关联的其他线索
        :param session_id: 会话ID
        :param clue_id: 线索ID
        :return: 相关线索列表
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        clue = next((c for c in session.collected_clues if c.clue_id == clue_id), None)
        if not clue:
            raise ClueNotFoundException()

        # 查找相关线索（基于关联嫌疑人）
        related_clues = []
        for c in session.collected_clues:
            if c.clue_id != clue_id and set(c.related_suspects) & set(clue.related_suspects):
                related_clues.append(c)

        return related_clues

    @staticmethod
    def associate_clues(session_id: str, clue_ids: List[str]) -> Dict[str, Any]:
        """
        关联多个线索
        :param session_id: 会话ID
        :param clue_ids: 要关联的线索ID列表
        :return: 关联结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if len(clue_ids) < 2:
            return {
                "success": False,
                "message": "至少需要选择两个线索才能关联",
            }

        # 验证所有线索都已收集
        collected_clue_ids = {c.clue_id for c in session.collected_clues}
        for clue_id in clue_ids:
            if clue_id not in collected_clue_ids:
                raise ClueNotFoundException(f"线索 {clue_id} 未找到或未收集")

        # 检查这些线索是否可以关联（有共同的嫌疑人）
        clues = [c for c in session.collected_clues if c.clue_id in clue_ids]
        common_suspects = set.intersection(*[set(c.related_suspects) for c in clues])

        if not common_suspects:
            return {
                "success": False,
                "message": "这些线索之间没有关联",
                "common_suspects": [],
            }

        # 更新线索状态为已关联
        for clue in clues:
            if clue.status != ClueStatus.ASSOCIATED:
                clue.status = ClueStatus.ASSOCIATED

        session_service.update_session(session)

        logger.info(f"会话 {session_id} 成功关联线索: {clue_ids}, 共同嫌疑人: {common_suspects}")

        return {
            "success": True,
            "message": f"线索关联成功！这些线索共同指向嫌疑人: {', '.join(common_suspects)}",
            "common_suspects": list(common_suspects),
            "associated_clues": clue_ids,
        }

    @staticmethod
    def get_undiscovered_clue_hints(session_id: str) -> List[Dict[str, Any]]:
        """
        获取未发现线索的提示（用于卡关时）
        :param session_id: 会话ID
        :return: 提示列表
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        # 找到未发现的线索
        undiscovered_clues = [
            clue for clue in session.case.clues
            if clue.status == ClueStatus.UNDISCOVERED
        ]

        hints = []
        for clue in undiscovered_clues[:3]:  # 最多给3个提示
            hints.append({
                "hint": f"在{clue.scene}似乎还有值得注意的东西...",
                "scene": clue.scene,
            })

        return hints

# 全局实例
clue_service = ClueService()
