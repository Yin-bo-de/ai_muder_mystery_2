"""会话管理服务：负责游戏会话的创建、存储、状态管理"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from collections import defaultdict

from app.core.config import settings
from app.core.constants import GameStatus
from app.models.case import Case
from app.models.game import GameSession, UserOperation, SuspectState, SuspectMood
from app.models.agent import Message
from app.utils.logger import logger

# 解决循环引用问题
GameSession.model_rebuild()

# 内存存储会话（开发阶段用，生产环境替换为Redis）
sessions: Dict[str, GameSession] = {}
# 用户会话映射
user_sessions: Dict[str, List[str]] = defaultdict(list)

class SessionService:
    """会话管理服务"""

    @staticmethod
    def create_session(user_id: str, case: Case) -> GameSession:
        """
        创建新的游戏会话
        :param user_id: 用户ID
        :param case: 生成的案件数据
        :return: 游戏会话对象
        """
        session_id = str(uuid.uuid4())

        session = GameSession(
            session_id=session_id,
            user_id=user_id,
            case=case,
            game_status=GameStatus.IN_PROGRESS,
            collected_clues=[],
            dialogue_history=[],
            suspect_states={
                suspect.suspect_id: SuspectState(
                    suspect_id=suspect.suspect_id,
                    pressure_level=0.0,
                    mood=SuspectMood.CALM,
                    lies_count=0
                )
                for suspect in case.suspects
            },
            user_operations=[],
            wrong_guess_count=0,
            start_time=datetime.now(),
            last_active_time=datetime.now(),
        )

        # 存储会话
        sessions[session_id] = session
        user_sessions[user_id].append(session_id)

        logger.info(f"创建新游戏会话: {session_id}, 用户: {user_id}, 案件: {case.case_id}")
        return session

    @staticmethod
    def get_session(session_id: str) -> Optional[GameSession]:
        """
        获取会话信息
        :param session_id: 会话ID
        :return: 会话对象，不存在返回None
        """
        session = sessions.get(session_id)
        if session:
            # 更新最后活跃时间
            session.last_active_time = datetime.now()
        return session

    @staticmethod
    def update_session(session: GameSession) -> bool:
        """
        更新会话信息
        :param session: 会话对象
        :return: 是否更新成功
        """
        if session.session_id not in sessions:
            logger.warning(f"尝试更新不存在的会话: {session.session_id}")
            return False

        session.last_active_time = datetime.now()
        sessions[session.session_id] = session
        return True

    @staticmethod
    def update_game_status(session_id: str, status: GameStatus) -> bool:
        """
        更新游戏状态
        :param session_id: 会话ID
        :param status: 新的游戏状态
        :return: 是否更新成功
        """
        session = sessions.get(session_id)
        if not session:
            logger.warning(f"尝试更新不存在的会话状态: {session_id}")
            return False

        session.game_status = status
        session.last_active_time = datetime.now()
        logger.info(f"会话 {session_id} 状态更新为: {status}")
        return True

    @staticmethod
    def add_user_operation(session_id: str, operation_type: str, detail: Dict = None, result: str = "success") -> bool:
        """
        添加用户操作记录
        :param session_id: 会话ID
        :param operation_type: 操作类型
        :param detail: 操作详情
        :param result: 操作结果，默认success
        :return: 是否添加成功
        """
        import uuid
        session = sessions.get(session_id)
        if not session:
            return False

        operation = UserOperation(
            operation_id=f"op_{uuid.uuid4().hex[:8]}",
            operation_type=operation_type,
            timestamp=datetime.now(),
            details=detail or {},
            result=result,
        )

        session.user_operations.append(operation)
        session.last_active_time = datetime.now()
        return True

    @staticmethod
    def add_dialogue_message(session_id: str, message: Message) -> bool:
        """
        添加对话消息到历史记录
        :param session_id: 会话ID
        :param message: 消息对象
        :return: 是否添加成功
        """
        session = sessions.get(session_id)
        if not session:
            return False

        session.dialogue_history.append(message)
        session.last_active_time = datetime.now()
        return True

    @staticmethod
    def increment_wrong_guess(session_id: str) -> int:
        """
        增加错误指认次数
        :param session_id: 会话ID
        :return: 当前错误次数
        """
        session = sessions.get(session_id)
        if not session:
            return -1

        session.wrong_guess_count += 1
        session.last_active_time = datetime.now()

        # 如果超过最大错误次数，游戏失败
        if session.wrong_guess_count >= settings.MAX_WRONG_GUESS:
            session.game_status = GameStatus.FAILED
            logger.info(f"会话 {session_id} 错误指认次数过多，游戏失败")

        return session.wrong_guess_count

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        删除会话
        :param session_id: 会话ID
        :return: 是否删除成功
        """
        if session_id in sessions:
            del sessions[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False

    @staticmethod
    def cleanup_expired_sessions() -> int:
        """
        清理过期会话（超过SESSION_EXPIRE_HOURS小时未活跃）
        :return: 清理的会话数量
        """
        now = datetime.now()
        expire_time = now - timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        expired_count = 0

        expired_sessions = [
            session_id for session_id, session in sessions.items()
            if session.last_active_time < expire_time
        ]

        for session_id in expired_sessions:
            del sessions[session_id]
            expired_count += 1

        if expired_count > 0:
            logger.info(f"清理过期会话 {expired_count} 个")

        return expired_count

    @staticmethod
    def get_user_sessions(user_id: str) -> List[GameSession]:
        """
        获取用户的所有会话
        :param user_id: 用户ID
        :return: 会话列表
        """
        session_ids = user_sessions.get(user_id, [])
        return [sessions[sid] for sid in session_ids if sid in sessions]

    @staticmethod
    def get_active_sessions_count() -> int:
        """获取当前活跃会话数量"""
        return len(sessions)

# 全局实例
session_service = SessionService()
