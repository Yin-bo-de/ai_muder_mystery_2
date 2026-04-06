"""
Agent相关数据模型
包含消息结构、角色配置、对话上下文
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"  # 用户
    ASSISTANT = "assistant"  # AI角色
    SYSTEM = "system"  # 系统消息
    FUNCTION = "function"  # 函数调用


class MessagePriority(int, Enum):
    """消息优先级枚举"""
    P0 = 0  # 最高优先级：用户直接提问/指令
    P1 = 1  # 高优先级：被点名/诬陷/出示不利证据/单独审讯
    P2 = 2  # 中优先级：主动发言（压力释放、剧情推进）
    P3 = 3  # 低优先级：自然互动、背景对话


class MessageType(str, Enum):
    """消息类型枚举"""
    TEXT = "text"  # 文本消息
    IMAGE = "image"  # 图片消息
    SYSTEM = "system"  # 系统提示
    ACTION = "action"  # 角色动作
    EVIDENCE = "evidence"  # 出示证据


class Message(BaseModel):
    """消息结构模型"""
    message_id: str = Field(..., description="消息唯一标识")
    role: MessageRole = Field(..., description="消息角色")
    sender_id: str = Field(..., description="发送者ID（用户或角色ID）")
    sender_name: str = Field(..., description="发送者名称")
    content: str = Field(..., description="消息内容")
    message_type: MessageType = Field(default=MessageType.TEXT, description="消息类型")
    priority: MessagePriority = Field(default=MessagePriority.P1, description="消息优先级")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="发送时间")
    reference_clues: List[str] = Field(
        default_factory=list,
        description="引用的线索ID列表"
    )
    reference_messages: List[str] = Field(
        default_factory=list,
        description="引用的消息ID列表"
    )
    target_suspects: List[str] = Field(
        default_factory=list,
        description="目标嫌疑人ID列表（仅@指定角色的消息）"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="附加元数据"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message_id": "msg_001",
                "role": "user",
                "sender_id": "user_001",
                "sender_name": "玩家",
                "content": "你昨天晚上去哪里了？",
                "message_type": "text",
                "priority": 0,
                "timestamp": "2024-01-15T10:30:00",
                "target_suspects": ["suspect_001"]
            }
        }
    }


class RolePersona(BaseModel):
    """角色人设配置模型"""
    role_id: str = Field(..., description="角色唯一标识")
    name: str = Field(..., description="角色姓名")
    age: int = Field(..., description="角色年龄")
    gender: str = Field(..., description="角色性别")
    occupation: str = Field(..., description="角色职业")
    personality: List[str] = Field(
        default_factory=list,
        description="性格特征列表"
    )
    speaking_style: str = Field(..., description="说话风格描述")
    voice_characteristics: str = Field(..., description="声音特征描述")
    background_story: str = Field(..., description="角色背景故事")
    behavior_rules: List[str] = Field(
        default_factory=list,
        description="行为规则列表"
    )
    forbidden_topics: List[str] = Field(
        default_factory=list,
        description="禁忌话题列表"
    )
    language_style: str = Field(default="normal", description="语言风格")
    max_response_length: int = Field(default=500, description="最大回复长度")

    model_config = {
        "json_schema_extra": {
            "example": {
                "role_id": "suspect_001",
                "name": "李四",
                "age": 38,
                "gender": "女",
                "occupation": "家庭主妇",
                "personality": ["温柔", "内向", "有主见"],
                "speaking_style": "委婉、谨慎",
                "voice_characteristics": "柔和，语速适中",
                "background_story": "与死者结婚10年，婚后成为家庭主妇",
                "behavior_rules": [
                    "尽量避免直接回答敏感问题",
                    "受到压力时会变得紧张",
                    "会为自己的不在场证明辩护"
                ],
                "forbidden_topics": ["离婚财产分割", "与死者的争吵"],
                "max_response_length": 300
            }
        }
    }


class RoleConfiguration(BaseModel):
    """角色配置模型"""
    persona: RolePersona = Field(..., description="角色人设")
    knowledge_base: Dict[str, str] = Field(
        default_factory=dict,
        description="角色知识库，key为主题，value为详细信息"
    )
    dialogue_history: List[Message] = Field(
        default_factory=list,
        description="角色记忆中的对话历史"
    )
    known_clues: List[str] = Field(
        default_factory=list,
        description="角色已知的线索ID列表"
    )
    hidden_information: List[str] = Field(
        default_factory=list,
        description="角色隐藏的信息（按隐瞒程度排序）"
    )
    behavior_parameters: Dict[str, float] = Field(
        default_factory=dict,
        description="行为参数（压力敏感系数、说谎概率等）"
    )
    communication_rules: Dict[str, Any] = Field(
        default_factory=dict,
        description="沟通规则"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "knowledge_base": {
                    "案件": "张三死于办公室，自己是嫌疑人之一",
                    "不在场证明": "案发时在商场购物，有监控记录"
                },
                "known_clues": ["clue_001", "clue_002"],
                "hidden_information": ["长期遭受家暴", "偷偷转移财产"],
                "behavior_parameters": {
                    "pressure_sensitivity": 0.8,
                    "lie_probability": 0.6,
                    "response_speed": 1.2
                }
            }
        }
    }


class DialogueContext(BaseModel):
    """对话上下文模型"""
    context_id: str = Field(..., description="上下文唯一标识")
    session_id: str = Field(..., description="会话ID")
    current_scene: str = Field(..., description="当前场景")
    dialogue_mode: str = Field(..., description="对话模式")
    active_roles: List[str] = Field(
        default_factory=list,
        description="当前活跃的角色ID列表"
    )
    message_history: List[Message] = Field(
        default_factory=list,
        description="对话历史记录"
    )
    clue_state: Dict[str, str] = Field(
        default_factory=dict,
        description="线索状态字典，key为clue_id，value为状态"
    )
    role_states: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="角色状态字典"
    )
    system_prompts: List[str] = Field(
        default_factory=list,
        description="系统提示信息"
    )
    context_window_size: int = Field(default=20, description="上下文窗口大小")
    last_interaction_time: datetime = Field(
        default_factory=datetime.utcnow,
        description="最后交互时间"
    )
    topic_tracking: Dict[str, Any] = Field(
        default_factory=dict,
        description="话题追踪信息"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "context_id": "ctx_001",
                "session_id": "session_001",
                "current_scene": "office",
                "dialogue_mode": "group",
                "active_roles": ["suspect_001", "suspect_002", "suspect_003", "suspect_004"],
                "context_window_size": 15,
                "topic_tracking": {
                    "current_topic": "不在场证明",
                    "discussion_count": 3,
                    "conflict_points": ["时间线不一致"]
                }
            }
        }
    }


class AgentPrompt(BaseModel):
    """Agent提示词模型"""
    template_id: str = Field(..., description="模板ID")
    template_type: str = Field(..., description="模板类型（system、user、assistant）")
    content: str = Field(..., description="提示词内容")
    variables: List[str] = Field(
        default_factory=list,
        description="模板变量列表"
    )
    version: str = Field(default="1.0", description="版本号")
    is_active: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "suspect_response_prompt",
                "template_type": "system",
                "content": "你是嫌疑人李四，现在正在接受警方调查。请按照你的人设回答问题...",
                "variables": ["character_name", "current_scene", "known_clues"],
                "version": "1.0",
                "is_active": True
            }
        }
    }


class AgentResponse(BaseModel):
    """Agent响应模型"""
    agent_id: str = Field(..., description="Agent标识")
    role_id: str = Field(..., description="对应的角色ID")
    response: Message = Field(..., description="生成的回复消息")
    reasoning_process: Optional[str] = Field(None, description="推理过程（调试用）")
    confidence_score: float = Field(default=0.8, description="回复置信度")
    mood_change: Optional[str] = Field(None, description="情绪变化")
    hidden_info_revealed: List[str] = Field(
        default_factory=list,
        description="暴露的隐藏信息"
    )
    pressure_change: float = Field(default=0.0, description="压力值变化")
    token_usage: Optional[Dict[str, int]] = Field(None, description="token使用情况")
    model_info: Optional[Dict[str, str]] = Field(None, description="使用的模型信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "agent_id": "agent_suspect_001",
                "role_id": "suspect_001",
                "response": {
                    "message_id": "msg_002",
                    "role": "assistant",
                    "sender_id": "suspect_001",
                    "sender_name": "李四",
                    "content": "我昨天晚上一直在商场购物，有监控可以证明。",
                    "timestamp": "2024-01-15T10:30:01"
                },
                "confidence_score": 0.85,
                "mood_change": "nervous",
                "pressure_change": 0.15,
                "model_info": {"name": "gpt-4", "version": "4.0"}
            }
        }
    }


class AgentRequest(BaseModel):
    """Agent请求模型"""
    agent_id: str = Field(..., description="Agent标识")
    session_id: str = Field(..., description="会话ID")
    role_id: str = Field(..., description="角色ID")
    context: DialogueContext = Field(..., description="对话上下文")
    user_message: Optional[Message] = Field(None, description="用户最新消息")
    system_prompt: Optional[str] = Field(None, description="系统提示")
    temperature: float = Field(default=0.7, description="生成温度")
    max_tokens: int = Field(default=500, description="最大生成token数")
    top_p: float = Field(default=0.9, description="核采样参数")
    stop_sequences: List[str] = Field(
        default_factory=list,
        description="停止序列"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "agent_id": "agent_suspect_001",
                "session_id": "session_001",
                "role_id": "suspect_001",
                "temperature": 0.6,
                "max_tokens": 300,
                "top_p": 0.8
            }
        }
    }


class DialogueManagerConfig(BaseModel):
    """对话管理器配置模型"""
    max_response_delay: float = Field(default=2.0, description="最大响应延迟（秒）")
    message_priority_weights: Dict[MessagePriority, float] = Field(
        default_factory=dict,
        description="消息优先级权重"
    )
    character_response_rates: Dict[str, float] = Field(
        default_factory=dict,
        description="角色响应率（高优先级回复概率）"
    )
    conflict_detection_threshold: float = Field(default=0.7, description="矛盾检测阈值")
    interruption_limit: int = Field(default=2, description="插话次数限制")
    group_response_timeout: float = Field(default=30.0, description="全体回复超时时间")
    single_response_timeout: float = Field(default=15.0, description="单独回复超时时间")
    response_frequency_control: Dict[MessageType, float] = Field(
        default_factory=dict,
        description="响应频率控制"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "max_response_delay": 2.5,
                "message_priority_weights": {0: 1.0, 1: 0.8, 2: 0.5, 3: 0.2},
                "character_response_rates": {"suspect_001": 0.9, "suspect_002": 0.7},
                "conflict_detection_threshold": 0.65,
                "interruption_limit": 2,
                "group_response_timeout": 30.0
            }
        }
    }


class ResponseGenerationConfig(BaseModel):
    """回复生成配置模型"""
    temperature: float = Field(default=0.7, description="生成温度")
    max_response_length: int = Field(default=400, description="最大回复长度")
    min_response_length: int = Field(default=50, description="最小回复长度")
    response_style: str = Field(default="natural", description="回复风格")
    include_emotion: bool = Field(default=True, description="是否包含情绪表达")
    include_action: bool = Field(default=True, description="是否包含动作描述")
    allow_lying: bool = Field(default=True, description="是否允许说谎")
    truthfulness_threshold: float = Field(default=0.5, description="真实度阈值")

    model_config = {
        "json_schema_extra": {
            "example": {
                "temperature": 0.6,
                "max_response_length": 350,
                "response_style": "natural",
                "include_emotion": True,
                "allow_lying": True,
                "truthfulness_threshold": 0.6
            }
        }
    }


class SenderIdentification(BaseModel):
    """发送者识别模型"""
    identifier_type: str = Field(..., description="识别类型")
    identifier_value: str = Field(..., description="识别值")
    confidence: float = Field(default=1.0, description="识别置信度")
    alternatives: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="替代识别结果"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "identifier_type": "username",
                "identifier_value": "suspect_001",
                "confidence": 0.95,
                "alternatives": [
                    {"identifier_type": "email", "identifier_value": "lisi@example.com"}
                ]
            }
        }
    }


class MessageReference(BaseModel):
    """消息引用模型"""
    reference_id: str = Field(..., description="引用的消息ID")
    reference_type: str = Field(..., description="引用类型（reply/forward）")
    reference_content: str = Field(..., description="引用的消息内容")

    model_config = {
        "json_schema_extra": {
            "example": {
                "reference_id": "msg_001",
                "reference_type": "reply",
                "reference_content": "你昨天晚上去哪里了？"
            }
        }
    }


class MessageContext(BaseModel):
    """消息上下文模型"""
    message_id: str = Field(..., description="消息ID")
    conversation_history: List[Message] = Field(
        default_factory=list,
        description="对话历史"
    )
    current_topic: str = Field(..., description="当前话题")
    speaker_topic_history: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="各角色的话题历史"
    )
    context_features: Dict[str, Any] = Field(
        default_factory=dict,
        description="上下文特征"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message_id": "msg_002",
                "current_topic": "不在场证明",
                "context_features": {"sentiment": "neutral", "urgency": "low"}
            }
        }
    }


class AgentSystemPrompt(BaseModel):
    """Agent系统提示模型"""
    prompt_id: str = Field(..., description="提示词ID")
    prompt_text: str = Field(..., description="提示词内容")
    priority: int = Field(default=1, description="优先级")
    dynamic_variables: List[str] = Field(
        default_factory=list,
        description="动态变量列表"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt_id": "system_prompt_1",
                "prompt_text": "你是一个专业的侦探助手，负责协助用户进行案件调查...",
                "priority": 1,
                "dynamic_variables": ["current_scene", "user_name"]
            }
        }
    }


class AgentPerformanceMetrics(BaseModel):
    """Agent性能指标模型"""
    total_interactions: int = Field(..., description="总交互次数")
    average_response_time: float = Field(..., description="平均响应时间（秒）")
    first_response_time: float = Field(..., description="首次响应时间（秒）")
    memory_utilization: float = Field(..., description="记忆使用率")
    token_usage: Dict[str, int] = Field(..., description="token使用统计")
    response_accuracy: float = Field(..., description="回复准确率")
    consistency_score: float = Field(..., description="一致性分数")
    context_relevance: float = Field(..., description="上下文相关性")
    conversation_completion_rate: float = Field(..., description="对话完成率")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_interactions": 156,
                "average_response_time": 1.8,
                "first_response_time": 0.9,
                "memory_utilization": 0.35,
                "token_usage": {"input": 12500, "output": 8500},
                "response_accuracy": 0.88,
                "consistency_score": 0.92,
                "context_relevance": 0.94,
                "conversation_completion_rate": 0.96
            }
        }
    }
