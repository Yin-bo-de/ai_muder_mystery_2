"""对话服务：消息处理、对话管理、AI交互逻辑"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.constants import DialogueMode, MessageRole, MessageType
from app.core.exceptions import SessionNotFoundException, GameCompletedException
from app.models.agent import Message
from .game_service import game_service
from .session_service import session_service
from app.utils.logger import logger

class DialogueService:
    """对话交互服务"""

    @staticmethod
    async def send_message(
        session_id: str,
        message: str,
        target_suspects: Optional[List[str]] = None,
        message_type: MessageType = MessageType.TEXT,
    ) -> Dict[str, Any]:
        """
        发送消息给AI角色
        :param session_id: 会话ID
        :param message: 消息内容
        :param target_suspects: 目标嫌疑人ID列表（@的角色）
        :param message_type: 消息类型
        :return: 回复结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if session.game_status != "in_progress":
            raise GameCompletedException()

        # 获取对话管理器
        dialogue_manager = game_service.get_dialogue_manager(session_id)
        if not dialogue_manager:
            raise SessionNotFoundException()

        # 保存用户消息到历史
        user_message = Message(
            role=MessageRole.USER,
            content=message,
            type=message_type,
            timestamp=datetime.now(),
        )
        session_service.add_dialogue_message(session_id, user_message)

        # 处理用户消息，获取嫌疑人回复
        responses, system_prompts = await dialogue_manager.process_user_message(
            message=message,
            target_suspects=target_suspects,
            is_accusation=message_type == MessageType.ACCUSATION,
            evidence_shown=message if message_type == MessageType.EVIDENCE else None,
        )

        # 保存嫌疑人回复到历史
        for resp in responses:
            suspect_message = Message(
                role=MessageRole.SUSPECT,
                content=resp["content"],
                sender_id=resp["suspect_id"],
                sender_name=resp["name"],
                mood=resp["mood"],
                type=MessageType.TEXT,
                timestamp=datetime.now(),
            )
            session_service.add_dialogue_message(session_id, suspect_message)

        # 保存系统提示到历史
        for prompt in system_prompts:
            system_message = Message(
                role=MessageRole.SYSTEM,
                content=prompt,
                type=MessageType.SYSTEM_PROMPT,
                timestamp=datetime.now(),
            )
            session_service.add_dialogue_message(session_id, system_message)

        # 更新会话嫌疑人状态
        session.suspect_states = {
            state["suspect_id"]: {
                "stress_level": state["stress_level"],
                "mood": state["mood"],
                "lied_count": state["lied_count"],
            }
            for state in dialogue_manager.get_suspect_state()
        }
        session_service.update_session(session)

        logger.info(f"会话 {session_id} 发送消息，收到 {len(responses)} 条回复")

        return {
            "success": True,
            "responses": responses,
            "system_prompts": system_prompts,
            "dialogue_mode": dialogue_manager.dialogue_mode,
        }

    @staticmethod
    def switch_interrogation_mode(
        session_id: str,
        mode: DialogueMode,
        suspect_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        切换审讯模式
        :param session_id: 会话ID
        :param mode: 模式：single/group
        :param suspect_id: 单独审讯的嫌疑人ID（single模式需要）
        :return: 切换结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if session.game_status != "in_progress":
            raise GameCompletedException()

        dialogue_manager = game_service.get_dialogue_manager(session_id)
        if not dialogue_manager:
            raise SessionNotFoundException()

        result = dialogue_manager.switch_interrogation_mode(mode, suspect_id)

        # 记录操作
        session_service.add_user_operation(
            session_id,
            "switch_mode",
            {"mode": mode, "suspect_id": suspect_id}
        )

        # 添加系统提示
        system_message = Message(
            role=MessageRole.SYSTEM,
            content=result["message"],
            type=MessageType.SYSTEM_PROMPT,
            timestamp=datetime.now(),
        )
        session_service.add_dialogue_message(session_id, system_message)

        return result

    @staticmethod
    def execute_control_command(session_id: str, command: str) -> Dict[str, Any]:
        """
        执行控场指令
        :param session_id: 会话ID
        :param command: 指令内容：keep_quiet/let_speak/summarize/restart
        :return: 执行结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if session.game_status != "in_progress":
            raise GameCompletedException()

        command_handlers = {
            "keep_quiet": lambda: "所有嫌疑人保持安静，现在听侦探提问！",
            "let_speak": lambda: "现在请大家自由发言，说说各自的看法。",
            "summarize": lambda: "好的，我来总结一下目前的线索和大家的证词...",
            "restart": lambda: "我们重新梳理一下案件经过...",
        }

        handler = command_handlers.get(command.lower())
        if not handler:
            return {
                "success": False,
                "message": f"未知指令: {command}",
            }

        result_message = handler()

        # 添加系统提示
        system_message = Message(
            role=MessageRole.SYSTEM,
            content=result_message,
            type=MessageType.SYSTEM_PROMPT,
            timestamp=datetime.now(),
        )
        session_service.add_dialogue_message(session_id, system_message)

        logger.info(f"会话 {session_id} 执行控场指令: {command}")

        return {
            "success": True,
            "result": result_message,
            "command": command,
        }

    @staticmethod
    def get_dialogue_history(
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        获取对话历史
        :param session_id: 会话ID
        :param limit: 分页大小
        :param offset: 偏移量
        :return: 对话历史
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        history = session.dialogue_history
        total = len(history)

        # 分页
        start = max(0, total - limit - offset) if limit > 0 else 0
        end = total - offset
        paginated_history = history[start:end]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "messages": [msg.dict() for msg in paginated_history],
        }

    @staticmethod
    def get_suspect_states(session_id: str) -> List[Dict[str, Any]]:
        """
        获取所有嫌疑人的状态
        :param session_id: 会话ID
        :return: 嫌疑人状态列表
        """
        dialogue_manager = game_service.get_dialogue_manager(session_id)
        if not dialogue_manager:
            raise SessionNotFoundException()

        return dialogue_manager.get_suspect_state()

    @staticmethod
    def clear_dialogue_history(session_id: str) -> bool:
        """
        清空对话历史（测试用）
        :param session_id: 会话ID
        :return: 是否清空成功
        """
        session = session_service.get_session(session_id)
        if not session:
            return False

        session.dialogue_history = []
        session_service.update_session(session)

        # 同时清空嫌疑人Agent的记忆
        dialogue_manager = game_service.get_dialogue_manager(session_id)
        if dialogue_manager:
            dialogue_manager.reset()

        logger.info(f"会话 {session_id} 对话历史已清空")
        return True

# 全局实例
dialogue_service = DialogueService()
