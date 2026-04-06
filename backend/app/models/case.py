"""
案件相关数据模型
包含死者信息、嫌疑人信息、线索信息、证据链、完整Case模型
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.core.constants import ClueType, ClueStatus


class Victim(BaseModel):
    """死者信息模型"""
    victim_id: str = Field(..., description="死者唯一标识", example="victim_001")
    name: str = Field(..., description="死者姓名", example="张三")
    age: int = Field(..., description="死者年龄", example=45)
    gender: str = Field(..., description="死者性别", example="男")
    occupation: str = Field(..., description="死者职业", example="企业老板")
    description: str = Field(..., description="死者外貌、性格描述", example="中等身材，性格强势")
    cause_of_death: str = Field(..., description="死因", example="锐器刺入心脏")
    death_time: datetime = Field(..., description="推定死亡时间")
    death_location: str = Field(..., description="死亡地点", example="张三的办公室")
    social_relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="社会关系字典，key为关系人ID，value为关系描述",
        example={"suspect_001": "妻子", "suspect_002": "合作伙伴"}
    )
    background_story: str = Field(..., description="死者背景故事", example="白手起家的企业家，近年与多人有利益纠纷")

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
    suspect_id: str = Field(..., description="嫌疑人唯一标识", example="suspect_001")
    name: str = Field(..., description="嫌疑人姓名", example="李四")
    age: int = Field(..., description="嫌疑人年龄", example=38)
    gender: str = Field(..., description="嫌疑人性别", example="女")
    occupation: str = Field(..., description="嫌疑人职业", example="家庭主妇")
    description: str = Field(..., description="嫌疑人外貌、性格描述", example="身材高挑，外表温柔")
    personality_traits: List[str] = Field(
        default_factory=list,
        description="性格特征列表",
        example=["温柔", "内向", "有主见"]
    )
    relationship_with_victim: str = Field(..., description="与死者关系", example="夫妻")
    motive: Optional[str] = Field(None, description="动机（仅真凶有完整动机，其他嫌疑人有潜在动机）", example="长期遭受家暴，为了离婚财产")
    alibi: str = Field(..., description="不在场证明", example="案发时在商场购物，有监控记录")
    alibi_reliability: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="不在场证明可信度，0.0-1.0",
        example=0.3
    )
    timeline: Dict[str, str] = Field(
        default_factory=dict,
        description="时间线字典，key为时间，value为活动描述",
        example={
            "18:00": "在家做饭",
            "19:00": "离开家去商场",
            "20:00": "在商场购物",
            "21:00": "离开商场回家"
        }
    )
    secrets: List[str] = Field(
        default_factory=list,
        description="隐藏的秘密列表（按隐瞒程度排序）",
        example=["长期遭受家暴", "偷偷转移财产", "案发前与死者发生争吵"]
    )
    is_murderer: bool = Field(default=False, description="是否为真凶", example=False)
    avatar: str = Field(default="", description="嫌疑人头像URL", example="https://example.com/avatar/suspect_001.jpg")
    background_story: str = Field(..., description="嫌疑人背景故事", example="与死者结婚10年，婚后成为家庭主妇")

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
    clue_id: str = Field(..., description="线索唯一标识", example="clue_001")
    name: str = Field(..., description="线索名称", example="带血的水果刀")
    clue_type: ClueType = Field(..., description="线索类型", example=ClueType.PHYSICAL)
    status: ClueStatus = Field(default=ClueStatus.HIDDEN, description="线索状态", example=ClueStatus.HIDDEN)
    description: str = Field(..., description="线索描述", example="一把沾有血迹的水果刀，刀柄上有指纹")
    location: str = Field(..., description="线索所在位置", example="办公室书桌抽屉")
    scene: str = Field(..., description="所属场景", example="办公室")
    content: Optional[str] = Field(None, description="线索具体内容（证词内容、文件内容等）", example="刀上的指纹属于嫌疑人李四")
    hidden_content: Optional[str] = Field(None, description="隐藏内容（解密后显示）", example="刀上还有第三人的指纹")
    related_clues: List[str] = Field(
        default_factory=list,
        description="关联的线索ID列表",
        example=["clue_002", "clue_003"]
    )
    required_password: Optional[str] = Field(None, description="解密密码（如需解密）", example="123456")
    required_clues: List[str] = Field(
        default_factory=list,
        description="解锁需要的关联线索ID列表",
        example=["clue_002"]
    )
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="线索重要程度，0.0-1.0",
        example=0.9
    )
    points_to_suspect: Optional[str] = Field(None, description="指向的嫌疑人ID", example="suspect_001")
    related_suspects: List[str] = Field(
        default_factory=list,
        description="关联的嫌疑人ID列表",
        example=["suspect_001", "suspect_002"]
    )
    is_red_herring: bool = Field(default=False, description="是否为干扰性线索", example=False)

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
    clue_id: str = Field(..., description="线索ID", example="clue_001")
    description: str = Field(..., description="该线索在证据链中的作用描述", example="证明凶器是水果刀")
    connects_to: List[str] = Field(
        default_factory=list,
        description="连接的下一个线索ID列表",
        example=["clue_002"]
    )
    logical_order: int = Field(..., description="在证据链中的逻辑顺序", example=1)


class EvidenceChain(BaseModel):
    """证据链模型"""
    chain_id: str = Field(..., description="证据链唯一标识", example="chain_001")
    name: str = Field(..., description="证据链名称", example="核心证据链")
    description: str = Field(..., description="证据链描述", example="证明凶手身份的完整证据链")
    items: List[EvidenceChainItem] = Field(..., description="证据链节点列表")
    conclusion: str = Field(..., description="证据链指向的结论", example="嫌疑人李四是凶手")
    required_clues: List[str] = Field(
        default_factory=list,
        description="形成完整证据链需要的所有线索ID",
        example=["clue_001", "clue_002", "clue_003", "clue_004"]
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
    scene_id: str = Field(..., description="场景唯一标识", example="scene_office")
    name: str = Field(..., description="场景名称", example="办公室")
    description: str = Field(..., description="场景描述", example="死者的办公室，整齐但有打斗痕迹")
    items: List[str] = Field(
        default_factory=list,
        description="场景中的可勘查物品列表",
        example=["书桌", "椅子", "书架", "保险箱", "垃圾桶"]
    )
    is_crime_scene: bool = Field(default=False, description="是否为第一案发现场", example=True)
    is_locked: bool = Field(default=False, description="场景是否锁定，需要解锁才能进入", example=False)

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
    case_id: str = Field(..., description="案件唯一标识", example="case_20240115_001")
    title: str = Field(..., description="案件标题", example="办公室命案")
    difficulty: int = Field(default=1, ge=1, le=5, description="难度等级，1-5", example=2)
    theme: str = Field(default="modern", description="案件题材", example="modern")
    description: str = Field(..., description="案件简介", example="企业老板张三死于办公室，警方锁定了四名嫌疑人")
    victim: Victim = Field(..., description="死者信息")
    suspects: List[Suspect] = Field(..., description="嫌疑人列表")
    clues: List[Clue] = Field(..., description="所有线索列表")
    scenes: List[Scene] = Field(..., description="案发现场场景列表")
    evidence_chains: List[EvidenceChain] = Field(..., description="证据链列表")
    murderer_id: str = Field(..., description="真凶的嫌疑人ID", example="suspect_001")
    murder_weapon: str = Field(..., description="凶器", example="水果刀")
    murder_motive: str = Field(..., description="完整作案动机", example="长期遭受家暴，担心离婚分不到财产，遂起杀意")
    murder_method: str = Field(..., description="详细作案手法", example="以送文件为由进入办公室，趁死者不备拿出事先准备的水果刀刺向死者心脏")
    true_timeline: Dict[str, str] = Field(
        default_factory=dict,
        description="真实时间线",
        example={
            "19:30": "凶手到达办公楼",
            "19:45": "凶手进入死者办公室",
            "20:00": "凶手刺杀死者",
            "20:15": "凶手清理现场",
            "20:30": "凶手离开办公楼"
        }
    )
    red_herrings: List[str] = Field(
        default_factory=list,
        description="干扰剧情分支种子",
        example=["嫌疑人王五与死者有债务纠纷", "现场发现的陌生人指纹"]
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
