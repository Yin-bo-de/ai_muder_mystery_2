"""全局常量定义"""
from enum import Enum

class GameStatus(str, Enum):
    """游戏状态"""
    PREPARING = "preparing"  # 准备中
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败

class OperationType(str, Enum):
    """用户操作类型"""
    INVESTIGATE = "investigate"  # 勘查
    SEND_MESSAGE = "send_message"  # 发送消息
    ACCUSE = "accuse"  # 指认
    DECRYPT = "decrypt"  # 解密
    CHANGE_MODE = "change_mode"  # 切换模式
    COMMAND = "command"  # 执行指令

class DialogueMode(str, Enum):
    """对话模式"""
    SINGLE = "single"  # 单独审讯
    GROUP = "group"  # 全体质询

class SuspectMood(str, Enum):
    """嫌疑人情绪状态"""
    CALM = "calm"  # 镇定
    NERVOUS = "nervous"  # 紧张
    ANGRY = "angry"  # 愤怒
    SCARED = "scared"  # 害怕
    GUILTY = "guilty"  # 心虚

class ClueType(str, Enum):
    """线索类型枚举"""
    PHYSICAL = "physical"  # 物证
    TESTIMONY = "testimony"  # 证词
    ASSOCIATION = "association"  # 关联线索
    DECRYPT = "decrypt"  # 需解密线索
    DOCUMENT = "document"  # 文档类线索

class ClueStatus(str, Enum):
    """线索状态枚举"""
    HIDDEN = "hidden"  # 未发现（别名：UNDISCOVERED）
    UNDISCOVERED = "hidden"  # 未发现，兼容旧代码
    DISCOVERED = "discovered"  # 已发现但未收集
    COLLECTED = "collected"  # 已收集
    LOCKED = "locked"  # 已锁定（需解密）
    UNLOCKED = "unlocked"  # 已解锁
    DECRYPTED = "unlocked"  # 已解密，兼容旧代码
    ASSOCIATED = "associated"  # 已关联

class MessageRole(str, Enum):
    """消息角色"""
    SYSTEM = "system"  # 系统
    USER = "user"  # 用户
    SUSPECT = "suspect"  # 嫌疑人
    JUDGE = "judge"  # 裁判

class MessagePriority(int, Enum):
    """消息优先级"""
    P0 = 0  # 最高优先级（用户指令、直接提问）
    P1 = 1  # 高优先级（被点名、被出示证据）
    P2 = 2  # 普通优先级（主动发言）

class MessageType(str, Enum):
    """消息类型"""
    TEXT = "text"  # 文本消息
    SYSTEM_PROMPT = "system_prompt"  # 系统提示
    EVIDENCE = "evidence"  # 出示证据
    ACCUSATION = "accusation"  # 指控


class ContradictionType(str, Enum):
    """矛盾类型枚举"""
    TIMELINE = "timeline"  # 时间线矛盾
    SPATIAL = "spatial"  # 空间/视野关系矛盾
    EVIDENCE = "evidence"  # 证据矛盾

# 错误码定义
ERROR_CODE = {
    10001: "会话不存在",
    10002: "游戏已结束",
    10003: "参数错误",
    10004: "权限不足",
    20001: "案件生成失败",
    20002: "Agent响应超时",
    20003: "对话发送失败",
    30001: "线索不存在",
    30002: "线索无法解密",
    30003: "指认信息不完整",
    40001: "模型调用失败",
    40002: "API调用配额不足",
}
