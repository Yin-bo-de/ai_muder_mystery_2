"""游戏管理相关API"""
from fastapi import APIRouter, Body, Query
from typing import Any, Optional, List
from pydantic import BaseModel

from app.services.game_service import game_service
from app.services.clue_service import clue_service
from app.models.game import GameStatusResponse
from app.core.constants import ClueType

router = APIRouter()

# 请求模型
class CreateGameRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    difficulty: Optional[str] = "medium"

class InvestigateRequest(BaseModel):
    scene: str
    item: Optional[str] = None

class DecryptRequest(BaseModel):
    clue_id: str
    password: Optional[str] = None
    related_clues: Optional[List[str]] = None

class AccuseRequest(BaseModel):
    suspect_id: str
    motive: str
    modus_operandi: str
    evidence: List[str]

@router.post("/new", summary="创建新案件")
async def create_new_case(request: CreateGameRequest) -> Any:
    """创建新的游戏案件"""
    return await game_service.create_new_game(
        user_id=request.user_id,
        difficulty=request.difficulty
    )

@router.get("/{session_id}/status", summary="获取游戏状态", response_model=GameStatusResponse)
async def get_game_status(session_id: str) -> Any:
    """获取指定会话的游戏状态"""
    return game_service.get_game_status(session_id)

@router.post("/{session_id}/investigate", summary="提交勘查操作")
async def submit_investigation(session_id: str, request: InvestigateRequest) -> Any:
    """提交现场勘查操作"""
    return game_service.submit_investigation(
        session_id=session_id,
        scene=request.scene,
        item=request.item
    )

@router.post("/{session_id}/decrypt", summary="提交线索解密")
async def decrypt_clue(session_id: str, request: DecryptRequest) -> Any:
    """提交线索解密请求"""
    return game_service.decrypt_clue(
        session_id=session_id,
        clue_id=request.clue_id,
        password=request.password,
        related_clues=request.related_clues
    )

@router.post("/{session_id}/accuse", summary="提交指认")
async def submit_accusation(session_id: str, request: AccuseRequest) -> Any:
    """提交凶手指认"""
    return await game_service.submit_accusation(
        session_id=session_id,
        suspect_id=request.suspect_id,
        motive=request.motive,
        modus_operandi=request.modus_operandi,
        evidence=request.evidence
    )

@router.get("/{session_id}/clues", summary="获取已收集线索列表")
async def get_collected_clues(
    session_id: str,
    clue_type: Optional[ClueType] = Query(None, description="线索类型过滤"),
) -> Any:
    """获取用户已收集的所有线索"""
    return clue_service.get_collected_clues(
        session_id=session_id,
        clue_type=clue_type
    )

@router.get("/{session_id}/clues/{clue_id}", summary="获取线索详情")
async def get_clue_detail(session_id: str, clue_id: str) -> Any:
    """获取指定线索的详细信息"""
    return clue_service.get_clue_detail(
        session_id=session_id,
        clue_id=clue_id
    )

@router.get("/{session_id}/clues/statistics", summary="获取线索统计信息")
async def get_clue_statistics(session_id: str) -> Any:
    """获取线索收集统计信息"""
    return clue_service.get_clue_statistics(
        session_id=session_id
    )

@router.post("/{session_id}/clues/associate", summary="关联线索")
async def associate_clues(
    session_id: str,
    clue_ids: List[str] = Body(..., description="要关联的线索ID列表"),
) -> Any:
    """关联多个线索，发现它们之间的联系"""
    return clue_service.associate_clues(
        session_id=session_id,
        clue_ids=clue_ids
    )

@router.get("/{session_id}/clues/hints", summary="获取线索提示")
async def get_clue_hints(session_id: str) -> Any:
    """获取未发现线索的提示（卡关时使用）"""
    return clue_service.get_undiscovered_clue_hints(
        session_id=session_id
    )

