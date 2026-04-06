"""AI交互相关API"""
from fastapi import APIRouter, Body, Query
from typing import Any, Optional, List
from pydantic import BaseModel

from app.services.dialogue_service import dialogue_service
from app.core.constants import DialogueMode, MessageType

router = APIRouter()

# 请求模型
class SendMessageRequest(BaseModel):
    message: str
    target_suspects: Optional[List[str]] = None
    message_type: Optional[MessageType] = MessageType.TEXT

class SwitchModeRequest(BaseModel):
    mode: DialogueMode
    suspect_id: Optional[str] = None

class ControlCommandRequest(BaseModel):
    command: str

@router.post("/{session_id}/send", summary="发送消息")
async def send_message(session_id: str, request: SendMessageRequest) -> Any:
    """发送消息给AI角色"""
    return await dialogue_service.send_message(
        session_id=session_id,
        message=request.message,
        target_suspects=request.target_suspects,
        message_type=request.message_type
    )

@router.post("/{session_id}/mode", summary="切换审讯模式")
async def switch_interrogation_mode(session_id: str, request: SwitchModeRequest) -> Any:
    """切换审讯模式（单独/全体）"""
    return dialogue_service.switch_interrogation_mode(
        session_id=session_id,
        mode=request.mode,
        suspect_id=request.suspect_id
    )

@router.post("/{session_id}/command", summary="执行控场指令")
async def execute_control_command(session_id: str, request: ControlCommandRequest) -> Any:
    """执行控场指令：keep_quiet/let_speak/summarize/restart"""
    return dialogue_service.execute_control_command(
        session_id=session_id,
        command=request.command
    )

@router.get("/{session_id}/history", summary="获取对话历史")
async def get_dialogue_history(
    session_id: str,
    limit: int = Query(100, description="分页大小"),
    offset: int = Query(0, description="偏移量"),
) -> Any:
    """获取对话历史记录"""
    return dialogue_service.get_dialogue_history(
        session_id=session_id,
        limit=limit,
        offset=offset
    )

@router.get("/{session_id}/suspects/states", summary="获取嫌疑人状态")
async def get_suspect_states(session_id: str) -> Any:
    """获取所有嫌疑人的当前状态（压力值、情绪等）"""
    return dialogue_service.get_suspect_states(
        session_id=session_id
    )

@router.post("/{session_id}/clear", summary="清空对话历史", deprecated=True)
async def clear_dialogue_history(session_id: str) -> Any:
    """清空对话历史（仅测试用）"""
    success = dialogue_service.clear_dialogue_history(session_id)
    return {
        "success": success,
        "message": "对话历史已清空" if success else "清空失败"
    }

