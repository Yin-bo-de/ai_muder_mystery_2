"""
案件相关数据模型
包含死者信息、嫌疑人信息、线索信息、证据链、完整Case模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator

from app.core.constants import ClueType, ClueStatus, ContradictionType


class Victim(BaseModel):
    """死者信息模型"""
    victim_id: str = Field(..., description="死者唯一标识")
    name: str = Field(..., description="死者姓名")
    age: int = Field(..., description="死者年龄")
    gender: str = Field(..., description="死者性别")
    occupation: str = Field(..., description="死者职业")
    description: str = Field(..., description="死者外貌、性格描述")
    cause_of_death: str = Field(..., description="死因")
    death_time: datetime = Field(..., description="推定死亡时间")
    death_location: str = Field(..., description="死亡地点")
    social_relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="社会关系字典，key为关系人ID，value为关系描述"
    )
    background_story: str = Field(..., description="死者背景故事")

    model_config = {
        "json_schema_extra": {
            "example": {
                "victim_id": "victim_001",
                "name": "张三",
                "age": 45,
                "gender": "男",
                "occupation": "企业老板",
                "description": "中等身材，性格强势",
                "cause_of_death": "锐器刺入心脏",
                "death_time": "2024-01-15T20:30:00",
                "death_location": "张三的办公室",
                "social_relationships": {
                    "suspect_001": "妻子",
                    "suspect_002": "合作伙伴"
                },
                "background_story": "白手起家的企业家，近年与多人有利益纠纷"
            }
        }
    }


class Suspect(BaseModel):
    """嫌疑人信息模型"""
    suspect_id: str = Field(..., description="嫌疑人唯一标识")
    name: str = Field(..., description="嫌疑人姓名")
    age: int = Field(..., description="嫌疑人年龄")
    gender: str = Field(..., description="嫌疑人性别")
    occupation: str = Field(..., description="嫌疑人职业")
    description: str = Field(..., description="嫌疑人外貌、性格描述")
    personality_traits: List[str] = Field(
        default_factory=list,
        description="性格特征列表"
    )
    relationship_with_victim: str = Field(..., description="与死者关系")
    motive: Optional[str] = Field(None, description="动机（仅真凶有完整动机，其他嫌疑人有潜在动机）")
    alibi: str = Field(..., description="不在场证明")
    alibi_reliability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="不在场证明可信度，0.0-1.0"
    )
    timeline: Dict[str, str] = Field(
        default_factory=dict,
        description="时间线字典，key为时间，value为活动描述"
    )
    secrets: List[str] = Field(
        default_factory=list,
        description="隐藏的秘密列表（按隐瞒程度排序）"
    )
    is_murderer: bool = Field(default=False, description="是否为真凶")
    avatar: str = Field(default="", description="嫌疑人头像URL")
    background_story: str = Field(..., description="嫌疑人背景故事")
    refusal_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="反驳阈值（0-1，越高越难触发反驳）"
    )
    counter_evidence: List[str] = Field(
        default_factory=list,
        description="反驳证据列表"
    )
    personality_modifier: float = Field(
        default=1.0,
        ge=0.5,
        le=1.5,
        description="性格修正系数（暴躁/冲动型>1.0，冷静/谨慎型<1.0）"
    )
    spatial_relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="与其他地点/人物的空间关系"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "suspect_id": "suspect_001",
                "name": "李四",
                "age": 38,
                "gender": "女",
                "occupation": "家庭主妇",
                "description": "身材高挑，外表温柔",
                "personality_traits": ["温柔", "内向", "有主见"],
                "relationship_with_victim": "夫妻",
                "motive": "长期遭受家暴，为了离婚财产",
                "alibi": "案发时在商场购物，有监控记录",
                "alibi_reliability": 0.3,
                "timeline": {
                    "18:00": "在家做饭",
                    "19:00": "离开家去商场",
                    "20:00": "在商场购物",
                    "21:00": "离开商场回家"
                },
                "secrets": ["长期遭受家暴", "偷偷转移财产", "案发前与死者发生争吵"],
                "is_murderer": False,
                "avatar": "",
                "background_story": "与死者结婚10年，婚后成为家庭主妇"
            }
        }
    }


class Clue(BaseModel):
    """线索信息模型"""
    clue_id: str = Field(..., description="线索唯一标识")
    name: str = Field(..., description="线索名称")
    clue_type: ClueType = Field(..., description="线索类型")
    status: ClueStatus = Field(default=ClueStatus.HIDDEN, description="线索状态")
    description: str = Field(..., description="线索描述")
    location: str = Field(..., description="线索所在位置")
    scene: str = Field(..., description="所属场景")
    content: Optional[str] = Field(default=None, description="线索具体内容（证词内容、文件内容等）")
    hidden_content: Optional[str] = Field(default=None, description="隐藏内容（解密后显示）")
    related_clues: List[str] = Field(
        default_factory=list,
        description="关联的线索ID列表"
    )
    required_password: Optional[str] = Field(default=None, description="解密密码（如需解密）")
    required_clues: List[str] = Field(
        default_factory=list,
        description="解锁需要的关联线索ID列表"
    )
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="线索重要程度，0.0-1.0"
    )
    points_to_suspect: Optional[str] = Field(default=None, description="指向的嫌疑人ID")
    related_suspects: List[str] = Field(
        default_factory=list,
        description="关联的嫌疑人ID列表"
    )
    is_red_herring: bool = Field(default=False, description="是否为干扰性线索")

    model_config = {
        "json_schema_extra": {
            "example": {
                "clue_id": "clue_001",
                "name": "带血的水果刀",
                "clue_type": "physical",
                "status": "hidden",
                "description": "一把沾有血迹的水果刀，刀柄上有指纹",
                "location": "办公室书桌抽屉",
                "scene": "office",
                "content": "刀上的指纹属于嫌疑人李四",
                "hidden_content": "刀上还有第三人的指纹",
                "related_clues": ["clue_002", "clue_003"],
                "required_password": None,
                "required_clues": ["clue_002"],
                "importance": 0.9,
                "points_to_suspect": "suspect_001",
                "is_red_herring": False
            }
        }
    }


class EvidenceChainItem(BaseModel):
    """证据链节点"""
    clue_id: str = Field(..., description="线索ID")
    description: str = Field(..., description="该线索在证据链中的作用描述")
    connects_to: List[str] = Field(
        default_factory=list,
        description="连接的下一个线索ID列表"
    )
    logical_order: int = Field(..., description="在证据链中的逻辑顺序")


class EvidenceChain(BaseModel):
    """证据链模型"""
    chain_id: str = Field(..., description="证据链唯一标识")
    name: str = Field(..., description="证据链名称")
    description: str = Field(..., description="证据链描述")
    items: List[EvidenceChainItem] = Field(..., description="证据链节点列表")
    conclusion: str = Field(..., description="证据链指向的结论")
    required_clues: List[str] = Field(
        default_factory=list,
        description="形成完整证据链需要的所有线索ID"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "chain_id": "chain_001",
                "name": "核心证据链",
                "description": "证明凶手身份的完整证据链",
                "items": [
                    {
                        "clue_id": "clue_001",
                        "description": "证明凶器是水果刀",
                        "connects_to": ["clue_002"],
                        "logical_order": 1
                    }
                ],
                "conclusion": "嫌疑人李四是凶手",
                "required_clues": ["clue_001", "clue_002", "clue_003", "clue_004"]
            }
        }
    }


class Scene(BaseModel):
    """案发现场场景模型"""
    scene_id: str = Field(..., description="场景唯一标识")
    name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")
    items: List[str] = Field(
        default_factory=list,
        description="场景中的可勘查物品列表"
    )
    is_crime_scene: bool = Field(default=False, description="是否为第一案发现场")
    is_locked: bool = Field(default=False, description="场景是否锁定，需要解锁才能进入")

    model_config = {
        "json_schema_extra": {
            "example": {
                "scene_id": "scene_office",
                "name": "办公室",
                "description": "死者的办公室，整齐但有打斗痕迹",
                "items": ["书桌", "椅子", "书架", "保险箱", "垃圾桶"],
                "is_crime_scene": True,
                "is_locked": False
            }
        }
    }


class Case(BaseModel):
    """完整案件模型"""
    case_id: str = Field(..., description="案件唯一标识")
    title: str = Field(..., description="案件标题")
    difficulty: int = Field(default=1, ge=1, le=5, description="难度等级，1-5")
    theme: str = Field(default="modern", description="案件题材")
    description: str = Field(..., description="案件简介")
    victim: Victim = Field(..., description="死者信息")
    suspects: List[Suspect] = Field(..., description="嫌疑人列表")
    clues: List[Clue] = Field(..., description="所有线索列表")
    scenes: List[Scene] = Field(..., description="案发现场场景列表")
    evidence_chains: List[EvidenceChain] = Field(..., description="证据链列表")
    murderer_id: str = Field(..., description="真凶的嫌疑人ID")
    murder_weapon: str = Field(..., description="凶器")
    murder_motive: str = Field(..., description="完整作案动机")
    murder_method: str = Field(..., description="详细作案手法")
    true_timeline: Dict[str, str] = Field(
        default_factory=dict,
        description="真实时间线"
    )
    red_herrings: List[str] = Field(
        default_factory=list,
        description="干扰剧情分支种子"
    )
    contradiction_points: List["ContradictionPoint"] = Field(
        default_factory=list,
        description="本案件的所有矛盾点"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, description="案件生成时间")

    model_config = {
        "json_schema_extra": {
            "example": {
                "case_id": "case_20240115_001",
                "title": "办公室命案",
                "difficulty": 2,
                "theme": "modern",
                "description": "企业老板张三死于办公室，警方锁定了四名嫌疑人",
                "murderer_id": "suspect_001",
                "murder_weapon": "水果刀",
                "murder_motive": "长期遭受家暴，担心离婚分不到财产，遂起杀意",
                "murder_method": "以送文件为由进入办公室，趁死者不备拿出事先准备的水果刀刺向死者心脏",
                "true_timeline": {
                    "19:30": "凶手到达办公楼",
                    "19:45": "凶手进入死者办公室",
                    "20:00": "凶手刺杀死者",
                    "20:15": "凶手清理现场",
                    "20:30": "凶手离开办公楼"
                },
                "red_herrings": ["嫌疑人王五与死者有债务纠纷", "现场发现的陌生人指纹"],
                "created_at": "2024-01-15T10:00:00"
            }
        }
    }


class CaseBasicInfo(BaseModel):
    """案件基础信息（返回给前端的公开信息）"""
    case_id: str = Field(..., description="案件唯一标识")
    title: str = Field(..., description="案件标题")
    description: str = Field(..., description="案件简介")
    victim_name: str = Field(..., description="死者姓名")
    suspect_count: int = Field(..., description="嫌疑人数量")
    scenes: List[Scene] = Field(..., description="可探索的场景列表")
    difficulty: int = Field(..., description="难度等级")

    model_config = {
        "json_schema_extra": {
            "example": {
                "case_id": "case_20240115_001",
                "title": "办公室命案",
                "description": "企业老板张三死于办公室，警方锁定了四名嫌疑人",
                "victim_name": "张三",
                "suspect_count": 4,
                "difficulty": 2
            }
        }
    }


class ContradictionPoint(BaseModel):
    """矛盾点模型"""
    contradiction_id: str = Field(..., description="矛盾点唯一标识")
    contradiction_type: ContradictionType = Field(..., description="矛盾类型")
    description: str = Field(..., description="矛盾描述")
    involved_suspects: List[str] = Field(
        default_factory=list,
        description="涉及的嫌疑人ID列表"
    )
    trigger_condition: Dict[str, Any] = Field(
        default_factory=dict,
        description="触发条件配置"
    )
    hint_for_user: Optional[str] = Field(
        default=None,
        description="给用户的系统提示文案"
    )
    related_clue_id: Optional[str] = Field(
        default=None,
        description="关联的线索ID（用户可勘查发现）"
    )
    clue_location: Optional[str] = Field(
        default=None,
        description="关联线索所在位置（用于生成线索）"
    )
    # 兼容LLM输出的字段
    trigger_keywords: Optional[List[str]] = Field(
        default=None,
        description="触发关键词数组（兼容LLM输出）"
    )
    requires_both_speaking: Optional[bool] = Field(
        default=None,
        description="是否需要两个嫌疑人都发言过才触发（兼容LLM输出）"
    )
    refuting_suspect: Optional[str] = Field(
        default=None,
        description="主动反驳的嫌疑人ID（兼容LLM输出）"
    )
    refutation_target: Optional[str] = Field(
        default=None,
        description="被反驳的嫌疑人ID（兼容LLM输出）"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "contradiction_id": "contradiction_001",
                "contradiction_type": "spatial",
                "description": "张小姐的卧室窗户能看到车库",
                "involved_suspects": ["suspect_001", "suspect_002"],
                "trigger_condition": {
                    "requires_both_speaking": True,
                    "keywords": ["车库", "没看到", "在卧室"]
                },
                "hint_for_user": "张小姐的卧室窗户能看到车库，但她说没看到任何人？",
                "related_clue_id": "clue_015",
                "clue_location": "张小姐卧室"
            }
        }
    }

    @model_validator(mode='after')
    def compat_llm_output(self):
        """兼容LLM输出的字段，自动转换和补全"""
        # 1. 从 trigger_keywords 和 requires_both_speaking 构建 trigger_condition
        if not self.trigger_condition:
            self.trigger_condition = {}

        if self.trigger_keywords is not None and "keywords" not in self.trigger_condition:
            self.trigger_condition["keywords"] = self.trigger_keywords

        if self.requires_both_speaking is not None and "requires_both_speaking" not in self.trigger_condition:
            self.trigger_condition["requires_both_speaking"] = self.requires_both_speaking

        # 2. 如果 hint_for_user 缺失，从 description 自动生成
        if not self.hint_for_user:
            self.hint_for_user = f"发现矛盾：{self.description}"

        return self

