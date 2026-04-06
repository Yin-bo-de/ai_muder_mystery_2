"""用户相关API"""
from fastapi import APIRouter, Query
from typing import Any, Optional

from app.services.session_service import session_service

router = APIRouter()

@router.get("/info", summary="获取用户信息")
async def get_user_info(user_id: Optional[str] = Query("default_user", description="用户ID")) -> Any:
    """获取当前用户信息"""
    # v1.0简化实现，后续接入用户系统
    user_sessions = session_service.get_user_sessions(user_id)
    solved_cases = len([s for s in user_sessions if s.game_status == "completed"])
    total_cases = len(user_sessions)

    # 计算侦探等级
    if solved_cases >= 20:
        rank = "传奇侦探"
    elif solved_cases >= 10:
        rank = "名侦探"
    elif solved_cases >= 5:
        rank = "优秀侦探"
    elif solved_cases >= 2:
        rank = "合格侦探"
    else:
        rank = "新手侦探"

    return {
        "user_id": user_id,
        "nickname": "侦探",
        "avatar": "",
        "solved_cases": solved_cases,
        "total_cases": total_cases,
        "rank": rank,
        "active_sessions": session_service.get_active_sessions_count(),
    }

@router.get("/history", summary="获取游戏历史")
async def get_game_history(user_id: Optional[str] = Query("default_user", description="用户ID")) -> Any:
    """获取用户游戏历史记录"""
    user_sessions = session_service.get_user_sessions(user_id)

    records = []
    for session in user_sessions:
        records.append({
            "session_id": session.session_id,
            "case_title": session.case.title,
            "case_id": session.case.case_id,
            "game_status": session.game_status,
            "play_time": int((session.last_active_time - session.start_time).total_seconds() / 60),
            "clue_completion_rate": int((len(session.collected_clues) / len(session.case.clues)) * 100) if session.case.clues else 0,
            "start_time": session.start_time.isoformat(),
            "end_time": session.last_active_time.isoformat() if session.game_status in ["completed", "failed"] else None,
        })

    return {
        "total": len(records),
        "records": sorted(records, key=lambda x: x["start_time"], reverse=True),
    }

@router.get("/statistics", summary="获取用户统计信息")
async def get_user_statistics(user_id: Optional[str] = Query("default_user", description="用户ID")) -> Any:
    """获取用户游戏统计信息"""
    user_sessions = session_service.get_user_sessions(user_id)
    total_cases = len(user_sessions)
    solved_cases = len([s for s in user_sessions if s.game_status == "completed"])
    failed_cases = len([s for s in user_sessions if s.game_status == "failed"])
    in_progress_cases = len([s for s in user_sessions if s.game_status == "in_progress"])

    total_play_time = sum(
        int((s.last_active_time - s.start_time).total_seconds() / 60)
        for s in user_sessions
    )

    average_clue_rate = 0
    if total_cases > 0:
        total_rate = sum(
            int((len(s.collected_clues) / len(s.case.clues)) * 100)
            for s in user_sessions if s.case.clues
        )
        average_clue_rate = int(total_rate / total_cases)

    return {
        "total_cases": total_cases,
        "solved_cases": solved_cases,
        "failed_cases": failed_cases,
        "in_progress_cases": in_progress_cases,
        "success_rate": int((solved_cases / total_cases) * 100) if total_cases > 0 else 0,
        "total_play_time_minutes": total_play_time,
        "average_clue_completion_rate": average_clue_rate,
    }

