"""
游戏相关数据模型
包含游戏状态枚举、会话信息、用户操作记录、嫌疑人状态
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class GameStatus(str, Enum):
    """游戏状态枚举"""
    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    SOLVED = "solved"  # 已结案（成功）
    FAILED = "failed"  # 已失败
    ABANDONED = "abandoned"  # 已放弃


class OperationType(str, Enum):
    """用户操作类型枚举"""
    INVESTIGATE = "investigate"  # 勘查线索
    SEND_MESSAGE = "send_message"  # 发送消息
    ACCUSE = "accuse"  # 指认凶手
    DECRYPT = "decrypt"  # 解密线索
    CHANGE_MODE = "change_mode"  # 切换模式
    COMMAND = "command"  # 执行指令


class DialogueMode(str, Enum):
    """对话模式枚举"""
    GROUP = "group"  # 全体质询
    SINGLE = "single"  # 单独审讯


class SuspectMood(str, Enum):
    """嫌疑人情绪状态枚举"""
    CALM = "calm"  # 镇定
    NERVOUS = "nervous"  # 紧张
    ANGRY = "angry"  # 愤怒
    GUILTY = "guilty"  # 心虚
    SAD = "sad"  # 悲伤
    SURPRISED = "surprised"  # 惊讶


class SuspectState(BaseModel):
    """嫌疑人状态模型"""
    suspect_id: str = Field(..., description="嫌疑人ID")
    mood: SuspectMood = Field(default=SuspectMood.CALM, description="当前情绪状态")
    pressure_level: float = Field(default=0.0, ge=0.0, le=1.0, description="压力值，0.0-1.0")
    lies_count: int = Field(default=0, description="说谎次数")
    secrets_revealed: List[str] = Field(
        default_factory=list,
        description="已暴露的秘密列表"
    )
    last_interaction_time: Optional[datetime] = Field(default=None, description="最后交互时间")
    answer_count: int = Field(default=0, description="回答次数")

    model_config = {
        "json_schema_extra": {
            "example": {
                "suspect_id": "suspect_001",
                "mood": "calm",
                "pressure_level": 0.2,
                "lies_count": 1,
                "secrets_revealed": ["长期遭受家暴"],
                "answer_count": 5
            }
        }
    }


class UserOperation(BaseModel):
    """用户操作记录模型"""
    operation_id: str = Field(..., description="操作ID")
    operation_type: OperationType = Field(..., description="操作类型")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="操作时间")
    target_id: Optional[str] = Field(default=None, description="操作目标ID（线索ID/嫌疑人ID/场景ID）")
    content: Optional[str] = Field(default=None, description="操作内容（消息内容/解密密码等）")
    result: str = Field(..., description="操作结果")
    details: Optional[Dict[str, Any]] = Field(default=None, description="详细信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "operation_id": "op_001",
                "operation_type": "investigate",
                "timestamp": "2024-01-15T10:30:00",
                "target_id": "clue_001",
                "content": None,
                "result": "success",
                "details": {"clue_name": "带血的水果刀"}
            }
        }
    }


class GameSession(BaseModel):
    """游戏会话信息模型"""
    session_id: str = Field(..., description="会话唯一标识")
    user_id: Optional[str] = Field(None, description="用户ID（未登录用户为None）")
    case: "Case" = Field(..., description="完整案件数据")
    game_status: GameStatus = Field(default=GameStatus.IN_PROGRESS, description="游戏状态")
    collected_clues: List[str] = Field(
        default_factory=list,
        description="已收集的线索ID列表"
    )
    dialogue_history: List["Message"] = Field(
        default_factory=list,
        description="完整对话历史（向后兼容）"
    )
    group_dialogue_history: List["Message"] = Field(
        default_factory=list,
        description="全体质询模式对话历史"
    )
    single_dialogue_histories: Dict[str, List["Message"]] = Field(
        default_factory=dict,
        description="各嫌疑人单独审讯对话历史，key为嫌疑人ID"
    )
    suspect_states: Dict[str, SuspectState] = Field(
        default_factory=dict,
        description="各嫌疑人状态字典，key为suspect_id"
    )
    user_operations: List[UserOperation] = Field(
        default_factory=list,
        description="用户操作记录列表"
    )
    wrong_guess_count: int = Field(default=0, description="错误指认次数")
    current_mode: DialogueMode = Field(default=DialogueMode.GROUP, description="当前对话模式")
    target_suspect: Optional[str] = Field(default=None, description="当前审讯的目标嫌疑人ID")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="游戏开始时间")
    last_active_time: datetime = Field(default_factory=datetime.utcnow, description="最后活跃时间")
    clue_reveal_count: int = Field(default=0, description="线索发现数量")
    reasoning_score: float = Field(default=0.0, ge=0.0, le=1.0, description="推理分数，0.0-1.0")
    refusal_count: int = Field(default=0, description="本轮对话已发生的反驳次数")
    last_refusal_reset: datetime = Field(default_factory=datetime.utcnow, description="上次重置反驳计数的时间")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session_001",
                "user_id": None,
                "game_status": "in_progress",
                "collected_clues": ["clue_001", "clue_002"],
                "wrong_guess_count": 1,
                "current_mode": "group",
                "start_time": "2024-01-15T10:00:00",
                "last_active_time": "2024-01-15T10:30:00",
                "clue_reveal_count": 5,
                "reasoning_score": 0.6
            }
        }
    }


class GameStatusResponse(BaseModel):
    """游戏状态响应模型（返回给前端）"""
    session_id: str = Field(..., description="会话ID")
    game_status: GameStatus = Field(..., description="游戏状态")
    case_basic: "CaseBasicInfo" = Field(..., description="案件基础信息")
    suspect_states: Dict[str, SuspectState] = Field(..., description="嫌疑人状态")
    collected_clue_count: int = Field(..., description="已收集线索数量")
    total_clue_count: int = Field(..., description="总线索数量")
    clue_reveal_count: int = Field(..., description="线索发现数量")
    wrong_guess_count: int = Field(..., description="错误指认次数")
    current_mode: DialogueMode = Field(..., description="当前对话模式")
    target_suspect: Optional[str] = Field(None, description="当前审讯目标")
    reasoning_score: float = Field(..., description="推理分数")
    elapsed_time: int = Field(..., description="已用时间（秒）")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "session_001",
                "game_status": "in_progress",
                "collected_clue_count": 5,
                "total_clue_count": 15,
                "clue_reveal_count": 8,
                "wrong_guess_count": 1,
                "current_mode": "group",
                "reasoning_score": 0.6,
                "elapsed_time": 1800
            }
        }
    }


class AccuseRequest(BaseModel):
    """指认凶手请求模型"""
    suspect_id: str = Field(..., description="被指认的嫌疑人ID")
    motive: str = Field(..., description="作案动机")
    modus_operandi: str = Field(..., description="作案手法")
    selected_evidence: List[str] = Field(..., description="选中的证据列表（线索ID）")
    reasoning: Optional[str] = Field(None, description="详细推理过程")

    model_config = {
        "json_schema_extra": {
            "example": {
                "suspect_id": "suspect_001",
                "motive": "长期遭受家暴，担心离婚分不到财产",
                "modus_operandi": "以送文件为由进入办公室，趁死者不备刺杀",
                "selected_evidence": ["clue_001", "clue_002", "clue_003"],
                "reasoning": "根据线索分析，嫌疑人李四有明确的动机和作案条件"
            }
        }
    }


class AccuseResult(BaseModel):
    """指认结果模型"""
    is_correct: bool = Field(..., description="是否正确")
    true_murderer: str = Field(..., description="真凶ID")
    reasoning_accuracy: float = Field(..., description="推理准确率，0.0-1.0")
    report: str = Field(..., description="结案报告")
    case_reconstruction: str = Field(..., description="案件还原")
    highlight_points: List[str] = Field(..., description="推理亮点")
    missing_points: List[str] = Field(..., description="遗漏要点")

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_correct": False,
                "true_murderer": "suspect_002",
                "reasoning_accuracy": 0.4,
                "report": "您的指认不正确。虽然您识别出了部分线索，但关键证据链不完整。",
                "case_reconstruction": "真凶是嫌疑人王五，他因商业利益纠纷杀害了张三...",
                "highlight_points": ["识别出了凶器类型", "分析了部分动机"],
                "missing_points": ["忽略了不在场证明的漏洞", "未找到关键关联线索"]
            }
        }
    }


class InvestigationRequest(BaseModel):
    """勘查请求模型"""
    scene: str = Field(..., description="场景ID")
    item: str = Field(..., description="物品ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "scene": "scene_office",
                "item": "书桌"
            }
        }
    }


class InvestigationResult(BaseModel):
    """勘查结果模型"""
    success: bool = Field(..., description="是否成功")
    clue: Optional["Clue"] = Field(None, description="发现的线索信息")
    message: str = Field(..., description="系统提示信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "clue": {"clue_id": "clue_001", "name": "带血的水果刀"},
                "message": "您在书桌抽屉里发现了一把带血的水果刀"
            }
        }
    }


class DecryptRequest(BaseModel):
    """解密请求模型"""
    clue_id: str = Field(..., description="线索ID")
    password: Optional[str] = Field(None, description="解密密码")
    related_clues: Optional[List[str]] = Field(None, description="提供的关联线索ID")

    model_config = {
        "json_schema_extra": {
            "example": {
                "clue_id": "clue_004",
                "password": "123456",
                "related_clues": ["clue_002"]
            }
        }
    }


class DecryptResult(BaseModel):
    """解密结果模型"""
    success: bool = Field(..., description="是否成功")
    clue: Optional["Clue"] = Field(None, description="解密后的线索信息")
    message: str = Field(..., description="系统提示信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "clue": {"clue_id": "clue_004", "name": "加密文件"},
                "message": "解密成功！文件显示死者正在调查嫌疑人李四的财产转移"
            }
        }
    }


class ModeChangeRequest(BaseModel):
    """模式切换请求模型"""
    mode: DialogueMode = Field(..., description="目标对话模式")
    target_suspect: Optional[str] = Field(None, description="单独审讯的目标嫌疑人ID（仅SINGLE模式需要）")

    model_config = {
        "json_schema_extra": {
            "example": {
                "mode": "single",
                "target_suspect": "suspect_001"
            }
        }
    }


class ModeChangeResult(BaseModel):
    """模式切换结果模型"""
    success: bool = Field(..., description="是否成功")
    current_mode: DialogueMode = Field(..., description="当前模式")
    target_suspect: Optional[str] = Field(None, description="目标嫌疑人")
    message: str = Field(..., description="系统提示信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "current_mode": "single",
                "target_suspect": "suspect_001",
                "message": "已切换到单独审讯模式，正在审讯嫌疑人李四"
            }
        }
    }


class CommandRequest(BaseModel):
    """指令执行请求模型"""
    command: str = Field(..., description="指令内容")
    target_ids: Optional[List[str]] = Field(None, description="目标ID列表")

    model_config = {
        "json_schema_extra": {
            "example": {
                "command": "silence",
                "target_ids": ["suspect_002"]
            }
        }
    }


class CommandResult(BaseModel):
    """指令执行结果模型"""
    success: bool = Field(..., description="是否成功")
    command: str = Field(..., description="执行的指令")
    message: str = Field(..., description="系统提示信息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "command": "silence",
                "message": "嫌疑人王五已被禁言",
                "details": {"target": "suspect_002"}
            }
        }
    }


class GameStats(BaseModel):
    """游戏统计信息模型"""
    total_games: int = Field(..., description="总游戏次数")
    average_time: int = Field(..., description="平均游戏时长（秒）")
    success_rate: float = Field(..., description="成功结案率")
    average_score: float = Field(..., description="平均推理分数")
    favorite_themes: List[str] = Field(..., description="最受欢迎的题材")
    completed_difficulties: Dict[str, int] = Field(..., description="各难度完成次数")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_games": 125,
                "average_time": 3600,
                "success_rate": 0.68,
                "average_score": 0.72,
                "favorite_themes": ["modern", "mystery"],
                "completed_difficulties": {"1": 45, "2": 35, "3": 28, "4": 12, "5": 5}
            }
        }
    }
