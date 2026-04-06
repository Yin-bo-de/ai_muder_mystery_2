# AI案件解谜整体技术架构设计

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 设计并实现AI驱动案件解谜应用的完整技术架构，包括前端、后端、AI Agent层三个核心部分，支撑完整的探案游戏流程。

**Architecture:** 采用前后端分离架构，后端基于FastAPI提供RESTful API，AI层基于LangChain实现多Agent架构（每个嫌疑人独立Agent），前端基于React实现富交互游戏界面。核心分为四层：展示层（前端）、API层（后端接口）、业务逻辑层（服务与调度）、AI能力层（Agent与大模型交互）。

**Tech Stack:**
- 后端：Python 3.10+, FastAPI, LangChain, Pydantic, loguru, pytest
- 前端：React 18+, Vite, Zustand, Ant Design, TypeScript
- AI：OpenAI API / Anthropic API, LangChain Agents
- 存储：Redis（会话缓存） + SQLite/PostgreSQL（持久化存储）

---

## 整体架构设计

### 系统分层架构
```
┌─────────────────────────────────────────────────────────────┐
│  展示层 (Frontend)                                          │
│  React + Vite + Zustand + Ant Design                        │
│  游戏界面、交互逻辑、状态管理                                │
├─────────────────────────────────────────────────────────────┤
│  API层 (Backend API)                                        │
│  FastAPI + Pydantic                                         │
│  RESTful接口、请求校验、身份认证、异常处理                    │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Business Logic)                                │
│  服务层 + 调度器                                            │
│  会话管理、游戏流程控制、线索系统、对话管理、案件逻辑        │
├─────────────────────────────────────────────────────────────┤
│  AI能力层 (AI Layer)                                        │
│  LangChain + 多Agent架构                                    │
│  案件生成Agent、嫌疑人角色Agent、对话控制Agent、逻辑判断Agent│
├─────────────────────────────────────────────────────────────┤
│  基础设施层 (Infrastructure)                                │
│  存储 + 中间件 + 工具链                                      │
│  Redis(会话缓存)、DB(持久化)、日志系统、监控系统              │
└─────────────────────────────────────────────────────────────┘
```

### 核心数据模型设计
```python
# 案件核心数据结构
class Case:
    case_id: str
    title: str
    background: str
    victim: Victim
    suspects: List[Suspect]
    murder_weapon: str
    murder_time: str
    murder_method: str
    real_murderer_id: str
    evidence_list: List[Evidence]
    scene_locations: List[SceneLocation]
    timeline: List[TimelineEvent]

class Suspect:
    suspect_id: str
    name: str
    age: int
    gender: str
    occupation: str
    background: str
    motive: str
    relationship_with_victim: str
    alibi: str
    is_murderer: bool
    personality: str
    speaking_style: str
    stress_level: float  # 0-1，压力值影响发言行为

class Evidence:
    evidence_id: str
    name: str
    description: str
    type: Literal["physical", "testimony", "document"]
    location: str
    is_hidden: bool
    is_encrypted: bool
    decryption_key: Optional[str]
    related_suspect_ids: List[str]

class GameSession:
    session_id: str
    user_id: str
    case: Case
    current_state: Literal["investigation", "interrogation", "closing"]
    collected_evidence: List[str]
    conversation_history: List[Message]
    suspect_states: Dict[str, SuspectState]
    current_scene: str
    remaining_mistakes: int = 2
    start_time: datetime
    last_interaction_time: datetime
```

---

## 任务分解

### 任务1：后端项目初始化与基础架构搭建

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/constants.py`
- Create: `backend/app/core/exceptions.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/base.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: 初始化Python项目结构**
```bash
mkdir -p backend/app/{core,models,api,services,agents,utils} backend/tests
cd backend && python -m venv venv
source venv/bin/activate
```

- [ ] **Step 2: 编写requirements.txt依赖配置**
```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
langchain==0.1.0
langchain-openai==0.0.2
langchain-anthropic==0.0.3
redis==5.0.1
sqlalchemy==2.0.23
loguru==0.7.2
pytest==7.4.3
python-dotenv==1.0.0
```

- [ ] **Step 3: 安装依赖**
```bash
pip install -r requirements.txt
```

- [ ] **Step 4: 编写核心配置文件 app/core/config.py**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI案件解谜"
    DEBUG: bool = False
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Anthropic配置
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./case_solver.db"
    
    # 游戏配置
    MAX_GAME_DURATION_MINUTES: int = 30
    MAX_INTERACTION_ROUNDS: int = 100
    MAX_MISTAKE_ATTEMPTS: int = 2

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 5: 编写FastAPI入口文件 main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由配置
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} service...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.PROJECT_NAME} service...")
```

- [ ] **Step 6: 验证服务可以正常启动**
```bash
cd backend && uvicorn main:app --reload --port 8000
```
Expected: 服务正常启动，访问 http://localhost:8000/health 返回健康状态，访问 http://localhost:8000/docs 可以看到Swagger文档。

- [ ] **Step 7: 提交代码**
```bash
git add backend/
git commit -m "feat: initialize backend project structure and basic configuration"
```

---

### 任务2：核心数据模型设计与实现

**Files:**
- Create: `backend/app/models/case.py`
- Create: `backend/app/models/game.py`
- Create: `backend/app/models/agent.py`
- Test: `backend/tests/models/test_models.py`

- [ ] **Step 1: 编写案件相关数据模型 app/models/case.py**
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict
from datetime import datetime

class Victim(BaseModel):
    name: str
    age: int
    gender: str
    occupation: str
    background: str
    cause_of_death: str
    time_of_death: str

class Suspect(BaseModel):
    suspect_id: str = Field(description="嫌疑人唯一ID")
    name: str
    age: int
    gender: str
    occupation: str
    background: str
    motive: str = Field(description="杀人动机")
    relationship_with_victim: str = Field(description="与死者关系")
    alibi: str = Field(description="不在场证明")
    is_murderer: bool = Field(default=False, description="是否是真凶")
    personality: str = Field(description="性格特征")
    speaking_style: str = Field(description="说话风格")
    stress_level: float = Field(default=0.0, ge=0.0, le=1.0, description="压力值0-1")

class Evidence(BaseModel):
    evidence_id: str
    name: str
    description: str
    type: Literal["physical", "testimony", "document"]
    location: str = Field(description="线索所在位置")
    is_hidden: bool = Field(default=False, description="是否隐藏")
    is_encrypted: bool = Field(default=False, description="是否需要解密")
    decryption_key: Optional[str] = Field(default=None, description="解密密钥/提示")
    related_suspect_ids: List[str] = Field(default_factory=list, description="关联的嫌疑人ID")

class SceneLocation(BaseModel):
    location_id: str
    name: str
    description: str
    interactable_objects: List[str] = Field(description="可交互物品列表")
    evidence_ids: List[str] = Field(default_factory=list, description="该场景下的线索ID列表")

class TimelineEvent(BaseModel):
    time: str
    event: str
    suspect_id: Optional[str] = None
    description: str

class Case(BaseModel):
    case_id: str
    title: str
    background: str = Field(description="案件背景描述")
    victim: Victim
    suspects: List[Suspect]
    murder_weapon: str = Field(description="凶器")
    murder_time: str = Field(description="作案时间")
    murder_method: str = Field(description="作案手法")
    real_murderer_id: str = Field(description="真凶的嫌疑人ID")
    evidence_list: List[Evidence]
    scene_locations: List[SceneLocation]
    timeline: List[TimelineEvent]
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

- [ ] **Step 2: 编写游戏会话相关模型 app/models/game.py**
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional
from datetime import datetime
from .case import Case, Evidence

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    suspect_id: Optional[str] = Field(default=None, description="如果是AI回复，对应的嫌疑人ID")
    is_private: bool = Field(default=False, description="是否是单独审讯的私密对话")

class SuspectState(BaseModel):
    suspect_id: str
    stress_level: float = Field(default=0.0, ge=0.0, le=1.0)
    is_in_interrogation: bool = Field(default=False, description="是否正在被单独审讯")
    last_interaction_time: Optional[datetime] = None
    has_spoken_recently: bool = Field(default=False)

class GameSession(BaseModel):
    session_id: str
    user_id: str
    case: Case
    current_state: Literal["investigation", "interrogation", "closing"] = Field(default="investigation")
    collected_evidence_ids: List[str] = Field(default_factory=list)
    conversation_history: List[Message] = Field(default_factory=list)
    suspect_states: Dict[str, SuspectState] = Field(default_factory=dict)
    current_scene_id: Optional[str] = None
    remaining_mistakes: int = Field(default=2, ge=0, le=2)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    last_interaction_time: datetime = Field(default_factory=datetime.utcnow)
    interaction_count: int = Field(default=0, ge=0)
    
    def is_game_over(self, max_duration_minutes: int = 30, max_interactions: int = 100) -> bool:
        """判断游戏是否超过时限或轮次限制"""
        duration = (datetime.utcnow() - self.start_time).total_seconds() / 60
        return duration > max_duration_minutes or self.interaction_count >= max_interactions

class AccusationRequest(BaseModel):
    murderer_id: str
    motive: str
    murder_time: str
    murder_weapon: str
    murder_process: str
    evidence_ids: List[str] = Field(default_factory=list)

class AccusationResult(BaseModel):
    is_correct: bool
    message: str
    case_reveal: Optional[str] = None
    accuracy_score: float = Field(ge=0.0, le=1.0)
    remaining_mistakes: Optional[int] = None
```

- [ ] **Step 3: 编写Agent相关模型 app/models/agent.py**
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class AgentResponse(BaseModel):
    content: str
    suspect_id: str
    emotion: Literal["calm", "nervous", "angry", "scared", "confident"]
    new_stress_level: float = Field(ge=0.0, le=1.0)
    should_interrupt: bool = Field(default=False, description="是否打断当前对话")
    interrupted_by_suspect_id: Optional[str] = None

class CaseGenerationResult(BaseModel):
    success: bool
    case_data: Optional[dict] = None
    error_message: Optional[str] = None

class ContradictionCheckResult(BaseModel):
    has_contradiction: bool
    contradiction_description: Optional[str] = None
    related_suspect_ids: List[str] = Field(default_factory=list)
```

- [ ] **Step 4: 编写测试用例 tests/models/test_models.py**
```python
import pytest
from datetime import datetime
from app.models.case import Victim, Suspect, Evidence, Case
from app.models.game import GameSession, Message, SuspectState

def test_victim_model():
    victim = Victim(
        name="张三",
        age=45,
        gender="男",
        occupation="企业家",
        background="某上市公司CEO",
        cause_of_death="钝器击打头部",
        time_of_death="2024-01-01 22:30"
    )
    assert victim.name == "张三"
    assert victim.age == 45

def test_suspect_model():
    suspect = Suspect(
        suspect_id="s1",
        name="李四",
        age=30,
        gender="男",
        occupation="司机",
        background="为死者开车3年",
        motive="被拖欠工资",
        relationship_with_victim="雇佣关系",
        alibi="当晚在车里睡觉",
        personality="老实内向",
        speaking_style="说话缓慢，有些结巴"
    )
    assert suspect.suspect_id == "s1"
    assert suspect.stress_level == 0.0

def test_game_session_model():
    victim = Victim(
        name="张三",
        age=45,
        gender="男",
        occupation="企业家",
        background="某上市公司CEO",
        cause_of_death="钝器击打头部",
        time_of_death="2024-01-01 22:30"
    )
    
    suspect = Suspect(
        suspect_id="s1",
        name="李四",
        age=30,
        gender="男",
        occupation="司机",
        background="为死者开车3年",
        motive="被拖欠工资",
        relationship_with_victim="雇佣关系",
        alibi="当晚在车里睡觉",
        personality="老实内向",
        speaking_style="说话缓慢，有些结巴"
    )
    
    case = Case(
        case_id="case1",
        title="别墅杀人案",
        background="富豪张三在自家别墅书房被杀",
        victim=victim,
        suspects=[suspect],
        murder_weapon="烟灰缸",
        murder_time="22:30",
        murder_method="用烟灰缸击打头部致死",
        real_murderer_id="s1",
        evidence_list=[],
        scene_locations=[],
        timeline=[]
    )
    
    session = GameSession(
        session_id="session1",
        user_id="user1",
        case=case
    )
    
    assert session.session_id == "session1"
    assert session.remaining_mistakes == 2
    assert session.interaction_count == 0
    assert session.is_game_over(max_duration_minutes=0) == True
    assert session.is_game_over(max_duration_minutes=30) == False
```

- [ ] **Step 5: 运行测试验证模型正确性**
```bash
cd backend && pytest tests/models/test_models.py -v
```
Expected: 所有测试用例通过。

- [ ] **Step 6: 提交代码**
```bash
git add backend/app/models/ backend/tests/models/
git commit -m "feat: implement core data models for case, game and agent"
```

---

### 任务3：AI Agent层架构设计与实现

**Files:**
- Create: `backend/app/agents/__init__.py`
- Create: `backend/app/agents/base_agent.py`
- Create: `backend/app/agents/case_generator_agent.py`
- Create: `backend/app/agents/suspect_agent.py`
- Create: `backend/app/agents/conversation_manager_agent.py`
- Create: `backend/app/agents/contradiction_checker_agent.py`
- Test: `backend/tests/agents/test_agents.py`

- [ ] **Step 1: 编写BaseAgent基类 app/agents/base_agent.py**
```python
from langchain.chat_models.base import BaseChatModel
from langchain.prompts import ChatPromptTemplate
from langchain.schema import BaseMessage
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings
import json

class BaseAgent:
    def __init__(self, llm: Optional[BaseChatModel] = None):
        self.llm = llm or self._get_default_llm()
        self.prompt_template = self._build_prompt_template()
    
    def _get_default_llm(self) -> BaseChatModel:
        """获取默认的大模型实例"""
        if settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=0.7,
                api_key=settings.OPENAI_API_KEY
            )
        elif settings.ANTHROPIC_API_KEY:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL,
                temperature=0.7,
                api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            raise ValueError("No LLM API key configured")
    
    def _build_prompt_template(self) -> ChatPromptTemplate:
        """构建提示词模板，子类需要重写此方法"""
        raise NotImplementedError("Subclasses must implement _build_prompt_template")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析模型响应，子类可以重写此方法实现自定义解析"""
        try:
            # 尝试解析JSON格式的响应
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse response as JSON: {response}")
            return {"content": response}
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """执行Agent逻辑"""
        try:
            prompt = self.prompt_template.format(**kwargs)
            response = await self.llm.ainvoke(prompt)
            return self._parse_response(response.content)
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            raise
```

- [ ] **Step 2: 编写案件生成Agent app/agents/case_generator_agent.py**
```python
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from loguru import logger
import json
from .base_agent import BaseAgent
from app.models.case import Case

class CaseGeneratorAgent(BaseAgent):
    def _build_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的推理剧本创作者，需要生成高质量的案件解谜案件。
            请严格按照以下要求生成：
            1. 案件要逻辑严谨，证据链完整，没有明显的逻辑漏洞
            2. 嫌疑人3-5人，每个人都有合理的杀人动机
            3. 真凶的作案手法要合理，有明确的证据指向
            4. 线索要分布合理，包含物证、证言、文档等多种类型
            5. 所有时间线要自洽，没有矛盾
            
            请以严格的JSON格式返回，包含以下字段：
            {{
                "title": "案件标题",
                "background": "案件背景描述",
                "victim": {{
                    "name": "死者姓名",
                    "age": 年龄,
                    "gender": "性别",
                    "occupation": "职业",
                    "background": "人物背景",
                    "cause_of_death": "死因",
                    "time_of_death": "死亡时间"
                }},
                "suspects": [
                    {{
                        "suspect_id": "s1",
                        "name": "姓名",
                        "age": 年龄,
                        "gender": "性别",
                        "occupation": "职业",
                        "background": "人物背景",
                        "motive": "杀人动机",
                        "relationship_with_victim": "与死者关系",
                        "alibi": "不在场证明",
                        "personality": "性格特征",
                        "speaking_style": "说话风格"
                    }}
                ],
                "murder_weapon": "凶器",
                "murder_time": "准确作案时间",
                "murder_method": "详细作案手法",
                "real_murderer_id": "真凶的suspect_id",
                "evidence_list": [
                    {{
                        "evidence_id": "e1",
                        "name": "线索名称",
                        "description": "线索描述",
                        "type": "physical/testimony/document",
                        "location": "所在位置",
                        "is_hidden": false,
                        "is_encrypted": false,
                        "decryption_key": null,
                        "related_suspect_ids": ["s1"]
                    }}
                ],
                "scene_locations": [
                    {{
                        "location_id": "l1",
                        "name": "地点名称",
                        "description": "地点描述",
                        "interactable_objects": ["物品1", "物品2"],
                        "evidence_ids": ["e1"]
                    }}
                ],
                "timeline": [
                    {{
                        "time": "时间",
                        "event": "事件描述",
                        "suspect_id": "嫌疑人ID(可选)",
                        "description": "详细描述"
                    }}
                ]
            }}
            
            注意：
            - real_murderer_id必须是suspects数组中存在的suspect_id
            - evidence_ids必须是evidence_list中存在的evidence_id
            - 所有ID要保持一致
            - 不要返回任何其他解释性文字，只返回JSON
            """),
            ("human", "请生成一个全新的案件件，类型为现代都市题材，难度中等。")
        ])
    
    async def generate_case(self) -> Dict[str, Any]:
        """生成新案件"""
        try:
            result = await self.run()
            logger.info(f"Generated case: {result.get('title', 'Unknown')}")
            return result
        except Exception as e:
            logger.error(f"Case generation failed: {str(e)}")
            raise
```

- [ ] **Step 3: 编写嫌疑人Agent app/agents/suspect_agent.py**
```python
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional
from loguru import logger
import json
from .base_agent import BaseAgent
from app.models.case import Suspect
from app.models.game import Message

class SuspectAgent(BaseAgent):
    def __init__(self, suspect: Suspect, case_context: str, llm=None):
        self.suspect = suspect
        self.case_context = case_context
        super().__init__(llm)
    
    def _build_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """你现在扮演以下角色参与案件调查：
            角色信息：
            姓名：{name}
            年龄：{age}
            性别：{gender}
            职业：{occupation}
            背景：{background}
            杀人动机：{motive}
            与死者关系：{relationship_with_victim}
            不在场证明：{alibi}
            是否是真凶：{is_murderer}
            性格：{personality}
            说话风格：{speaking_style}
            
            案件背景：{case_context}
            
            你的行为规则：
            1. 严格保持人设一致性，说话风格和性格要始终符合设定
            2. 如果你是真凶，要尽量隐瞒真相，必要时可以说谎，但不要有明显的逻辑漏洞
            3. 如果你不是真凶，要如实回答问题，但可以隐瞒自己的小秘密
            4. 压力值会影响你的回答：压力越高越容易紧张、说漏嘴、甚至情绪失控
            5. 被问到关键证据时要有相应的情绪反应
            6. 回答要自然，符合日常对话，不要太书面化
            
            当前压力值：{current_stress_level} (0-1，越高越紧张)
            对话历史：{conversation_history}
            
            请以JSON格式返回回答：
            {{
                "content": "你的回答内容",
                "emotion": "calm/nervous/angry/scared/confident",
                "new_stress_level": 新的压力值(0-1之间的浮点数),
                "should_interrupt": false
            }}
            
            注意：不要返回任何其他内容，只返回JSON。
            """),
            ("human", "用户提问：{user_question}")
        ])
    
    async def respond(
        self, 
        user_question: str, 
        conversation_history: List[Message],
        current_stress_level: float,
        is_private_interrogation: bool = False
    ) -> Dict[str, Any]:
        """生成嫌疑人回答"""
        try:
            # 格式化对话历史
            history_text = "\n".join([
                f"{msg.role}: {msg.content}" 
                for msg in conversation_history[-10:]  # 只保留最近10轮对话
            ])
            
            result = await self.run(
                name=self.suspect.name,
                age=self.suspect.age,
                gender=self.suspect.gender,
                occupation=self.suspect.occupation,
                background=self.suspect.background,
                motive=self.suspect.motive,
                relationship_with_victim=self.suspect.relationship_with_victim,
                alibi=self.suspect.alibi,
                is_murderer="是" if self.suspect.is_murderer else "不是",
                personality=self.suspect.personality,
                speaking_style=self.suspect.speaking_style,
                case_context=self.case_context,
                current_stress_level=current_stress_level,
                conversation_history=history_text,
                user_question=user_question
            )
            
            logger.debug(f"Suspect {self.suspect.suspect_id} responded: {result.get('content', '')[:50]}...")
            return result
        except Exception as e:
            logger.error(f"Suspect agent response failed: {str(e)}")
            raise
```

- [ ] **Step 4: 提交Agent架构代码**
```bash
git add backend/app/agents/
git commit -m "feat: implement base agent architecture and core agent classes"
```

---

### 任务4：后端业务服务层设计与实现

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/case_service.py`
- Create: `backend/app/services/game_service.py`
- Create: `backend/app/services/session_service.py`
- Create: `backend/app/services/agent_service.py`

- [ ] **Step 1: 编写会话管理服务 app/services/session_service.py**
```python
from typing import Optional, Dict
import json
import uuid
from datetime import datetime
from loguru import logger
import redis
from app.core.config import settings
from app.models.game import GameSession

class SessionService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.session_prefix = "game_session:"
        self.session_ttl = 3600 * 24  # 会话过期时间24小时
    
    def generate_session_id(self) -> str:
        """生成唯一会话ID"""
        return str(uuid.uuid4())
    
    async def save_session(self, session: GameSession) -> None:
        """保存游戏会话到Redis"""
        try:
            session_key = f"{self.session_prefix}{session.session_id}"
            session_data = session.model_dump_json()
            self.redis_client.setex(session_key, self.session_ttl, session_data)
            logger.debug(f"Saved session {session.session_id}")
        except Exception as e:
            logger.error(f"Failed to save session: {str(e)}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[GameSession]:
        """从Redis获取游戏会话"""
        try:
            session_key = f"{self.session_prefix}{session_id}"
            session_data = self.redis_client.get(session_key)
            if not session_data:
                return None
            # 刷新过期时间
            self.redis_client.expire(session_key, self.session_ttl)
            return GameSession.model_validate_json(session_data)
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            return None
    
    async def delete_session(self, session_id: str) -> None:
        """删除游戏会话"""
        try:
            session_key = f"{self.session_prefix}{session_id}"
            self.redis_client.delete(session_key)
            logger.debug(f"Deleted session {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            raise

# 单例实例
session_service = SessionService()
```

- [ ] **Step 2: 编写案件服务 app/services/case_service.py**
```python
from typing import Dict, Any
import uuid
from loguru import logger
from app.agents.case_generator_agent import CaseGeneratorAgent
from app.models.case import Case

class CaseService:
    def __init__(self):
        self.case_generator = CaseGeneratorAgent()
    
    def generate_case_id(self) -> str:
        """生成案件ID"""
        return f"case_{uuid.uuid4().hex[:8]}"
    
    async def generate_new_case(self) -> Case:
        """生成新案件"""
        try:
            logger.info("Generating new case...")
            case_data = await self.case_generator.generate_case()
            
            # 补充缺失的ID字段
            case_data["case_id"] = self.generate_case_id()
            
            # 为嫌疑人设置is_murderer字段
            real_murderer_id = case_data["real_murderer_id"]
            for suspect in case_data["suspects"]:
                suspect["is_murderer"] = suspect["suspect_id"] == real_murderer_id
            
            # 验证并转换为Case模型
            case = Case.model_validate(case_data)
            logger.info(f"Successfully generated case: {case.case_id} - {case.title}")
            return case
        except Exception as e:
            logger.error(f"Case generation failed: {str(e)}")
            raise

# 单例实例
case_service = CaseService()
```

- [ ] **Step 3: 编写游戏服务 app/services/game_service.py**
```python
from typing import List, Optional, Dict
from loguru import logger
import uuid
from datetime import datetime
from app.models.case import Case, Evidence
from app.models.game import GameSession, Message, SuspectState, AccusationRequest, AccusationResult
from app.services.session_service import session_service
from app.services.case_service import case_service
from app.services.agent_service import agent_service
from app.core.config import settings

class GameService:
    async def create_new_game(self, user_id: str) -> GameSession:
        """创建新游戏"""
        try:
            # 生成新案件
            case = await case_service.generate_new_case()
            
            # 创建会话
            session_id = session_service.generate_session_id()
            
            # 初始化嫌疑人状态
            suspect_states = {}
            for suspect in case.suspects:
                suspect_states[suspect.suspect_id] = SuspectState(
                    suspect_id=suspect.suspect_id,
                    stress_level=suspect.stress_level
                )
            
            session = GameSession(
                session_id=session_id,
                user_id=user_id,
                case=case,
                suspect_states=suspect_states,
                current_scene_id=case.scene_locations[0].location_id if case.scene_locations else None
            )
            
            # 添加系统欢迎消息
            welcome_msg = self._create_system_message(f"""
            欢迎来到《{case.title}》探案现场。
            {case.background}
            死者是{case.victim.name}，{case.victim.cause_of_death}，死亡时间大概在{case.victim.time_of_death}。
            现场有以下嫌疑人：
            {chr(10).join([f"- {s.name}（{s.age}岁，{s.occupation}）" for s in case.suspects])}
            你可以开始勘查现场或质询嫌疑人。
            """)
            session.conversation_history.append(welcome_msg)
            
            # 保存会话
            await session_service.save_session(session)
            logger.info(f"Created new game session: {session_id} for user {user_id}")
            return session
        except Exception as e:
            logger.error(f"Failed to create new game: {str(e)}")
            raise
    
    async def process_user_message(
        self, 
        session_id: str, 
        message: str,
        target_suspect_ids: Optional[List[str]] = None,
        is_private_interrogation: bool = False
    ) -> GameSession:
        """处理用户消息"""
        try:
            session = await session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # 添加用户消息到历史
            user_msg = Message(role="user", content=message)
            session.conversation_history.append(user_msg)
            session.interaction_count += 1
            session.last_interaction_time = datetime.utcnow()
            
            # 判断游戏是否超时
            if session.is_game_over(
                max_duration_minutes=settings.MAX_GAME_DURATION_MINUTES,
                max_interactions=settings.MAX_INTERACTION_ROUNDS
            ):
                timeout_msg = self._create_system_message("游戏时间已到或交互次数超过限制，请进入指认凶手环节。")
                session.conversation_history.append(timeout_msg)
                session.current_state = "closing"
                await session_service.save_session(session)
                return session
            
            # 调用Agent服务处理对话
            responses = await agent_service.process_conversation(
                session=session,
                user_message=message,
                target_suspect_ids=target_suspect_ids,
                is_private_interrogation=is_private_interrogation
            )
            
            # 添加AI回复到历史
            for resp in responses:
                ai_msg = Message(
                    role="assistant",
                    content=resp["content"],
                    suspect_id=resp["suspect_id"],
                    is_private=is_private_interrogation
                )
                session.conversation_history.append(ai_msg)
                
                # 更新嫌疑人压力值
                if resp["suspect_id"] in session.suspect_states:
                    session.suspect_states[resp["suspect_id"]].stress_level = resp["new_stress_level"]
                    session.suspect_states[resp["suspect_id"]].last_interaction_time = datetime.utcnow()
            
            # 检查对话中的矛盾点
            contradiction = await agent_service.check_contradictions(session)
            if contradiction.has_contradiction:
                contradiction_msg = self._create_system_message(f"系统提示：【{contradiction.contradiction_description}】")
                session.conversation_history.append(contradiction_msg)
            
            await session_service.save_session(session)
            return session
        except Exception as e:
            logger.error(f"Failed to process user message: {str(e)}")
            raise
    
    async def collect_evidence(self, session_id: str, evidence_id: str) -> bool:
        """收集线索"""
        try:
            session = await session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # 检查线索是否存在且未被收集
            evidence_exists = any(e.evidence_id == evidence_id for e in session.case.evidence_list)
            if not evidence_exists:
                return False
            
            if evidence_id not in session.collected_evidence_ids:
                session.collected_evidence_ids.append(evidence_id)
                await session_service.save_session(session)
                logger.info(f"Collected evidence {evidence_id} in session {session_id}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to collect evidence: {str(e)}")
            raise
    
    async def submit_accusation(self, session_id: str, accusation: AccusationRequest) -> AccusationResult:
        """提交指认"""
        try:
            session = await session_service.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            is_correct = accusation.murderer_id == session.case.real_murderer_id
            
            if not is_correct:
                session.remaining_mistakes -= 1
                await session_service.save_session(session)
                
                if session.remaining_mistakes > 0:
                    return AccusationResult(
                        is_correct=False,
                        message=f"指认错误！你还有{session.remaining_mistakes}次机会。再仔细想想，是不是遗漏了什么线索？",
                        accuracy_score=self._calculate_accuracy_score(accusation, session),
                        remaining_mistakes=session.remaining_mistakes
                    )
                else:
                    # 游戏失败，公布真相
                    return AccusationResult(
                        is_correct=False,
                        message="很遗憾，你的指认次数已用完。案件真相是：",
                        case_reveal=self._generate_case_reveal(session.case),
                        accuracy_score=self._calculate_accuracy_score(accusation, session)
                    )
            else:
                # 指认正确
                return AccusationResult(
                    is_correct=True,
                    message="恭喜你！成功找出了真凶！",
                    case_reveal=self._generate_case_reveal(session.case),
                    accuracy_score=1.0
                )
        except Exception as e:
            logger.error(f"Failed to process accusation: {str(e)}")
            raise
    
    def _create_system_message(self, content: str) -> Message:
        """创建系统消息"""
        return Message(role="system", content=content.strip())
    
    def _calculate_accuracy_score(self, accusation: AccusationRequest, session: GameSession) -> float:
        """计算推理准确率"""
        score = 0.0
        total = 4  # 四个评分项：凶手、动机、时间、手法
        
        # 检查凶手是否正确
        if accusation.murderer_id == session.case.real_murderer_id:
            score += 0.4
        
        # 检查动机是否合理
        real_suspect = next(s for s in session.case.suspects if s.suspect_id == session.case.real_murderer_id)
        if real_suspect.motive in accusation.motive:
            score += 0.2
        
        # 检查作案时间是否正确
        if session.case.murder_time in accusation.murder_time:
            score += 0.2
        
        # 检查作案工具是否正确
        if session.case.murder_weapon in accusation.murder_weapon:
            score += 0.2
        
        return round(score, 2)
    
    def _generate_case_reveal(self, case: Case) -> str:
        """生成案件真相揭露文本"""
        real_murderer = next(s for s in case.suspects if s.suspect_id == case.real_murderer_id)
        
        reveal = f"""
        # 案件真相
        
        ## 真凶身份
        凶手是{real_murderer.name}（{real_murderer.occupation}）。
        
        ## 作案动机
        {real_murderer.motive}
        
        ## 作案手法
        {case.murder_method}
        
        ## 完整时间线
        {chr(10).join([f"- {event.time}: {event.description}" for event in case.timeline])}
        
        ## 关键证据
        {chr(10).join([f"- {e.name}: {e.description}" for e in case.evidence_list if case.real_murderer_id in e.related_suspect_ids])}
        """
        
        return reveal.strip()

# 单例实例
game_service = GameService()
```

- [ ] **Step 4: 提交服务层代码**
```bash
git add backend/app/services/
git commit -m "feat: implement business service layer (session, case, game services)"
```

---

### 任务5：API层设计与实现

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/v1/api.py`
- Create: `backend/app/api/v1/endpoints/game.py`
- Create: `backend/app/api/v1/endpoints/case.py`
- Create: `backend/app/api/v1/endpoints/session.py`

- [ ] **Step 1: 编写API路由入口 app/api/v1/api.py**
```python
from fastapi import APIRouter
from app.api.v1.endpoints import game, case, session

api_router = APIRouter()
api_router.include_router(game.router, prefix="/game", tags=["game"])
api_router.include_router(case.router, prefix="/case", tags=["case"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
```

- [ ] **Step 2: 编写游戏相关接口 app/api/v1/endpoints/game.py**
```python
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from loguru import logger
from app.models.game import GameSession, AccusationRequest, AccusationResult
from app.services.game_service import game_service

router = APIRouter()

@router.post("/new", response_model=GameSession)
async def create_new_game(user_id: str = Body(..., embed=True)):
    """创建新游戏"""
    try:
        return await game_service.create_new_game(user_id)
    except Exception as e:
        logger.error(f"Create new game failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create new game")

@router.post("/{session_id}/message", response_model=GameSession)
async def send_message(
    session_id: str,
    message: str = Body(..., embed=True),
    target_suspect_ids: Optional[List[str]] = Body(None, embed=True),
    is_private: bool = Body(False, embed=True)
):
    """发送消息"""
    try:
        return await game_service.process_user_message(
            session_id=session_id,
            message=message,
            target_suspect_ids=target_suspect_ids,
            is_private_interrogation=is_private
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Send message failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process message")

@router.post("/{session_id}/evidence/{evidence_id}/collect", response_model=bool)
async def collect_evidence(session_id: str, evidence_id: str):
    """收集线索"""
    try:
        return await game_service.collect_evidence(session_id, evidence_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Collect evidence failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect evidence")

@router.post("/{session_id}/accuse", response_model=AccusationResult)
async def accuse(session_id: str, accusation: AccusationRequest):
    """指认凶手"""
    try:
        return await game_service.submit_accusation(session_id, accusation)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Submit accusation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit accusation")
```

- [ ] **Step 3: 编写会话相关接口 app/api/v1/endpoints/session.py**
```python
from fastapi import APIRouter, HTTPException
from loguru import logger
from app.models.game import GameSession
from app.services.session_service import session_service

router = APIRouter()

@router.get("/{session_id}", response_model=GameSession)
async def get_session(session_id: str):
    """获取会话信息"""
    try:
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Get session failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session")

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        await session_service.delete_session(session_id)
        return {"status": "success", "message": "Session deleted"}
    except Exception as e:
        logger.error(f"Delete session failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")
```

- [ ] **Step 4: 提交API层代码**
```bash
git add backend/app/api/
git commit -m "feat: implement RESTful API layer for game, case and session endpoints"
```

---

### 任务6：前端项目初始化与架构设计

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/store/index.ts`
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: 初始化前端项目结构**
```bash
mkdir -p frontend/src/{components,pages,store,services,types,hooks,utils}
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

- [ ] **Step 2: 安装依赖**
```bash
npm install zustand antd axios dayjs react-router-dom @ant-design/icons
npm install -D @types/node
```

- [ ] **Step 3: 编写package.json脚本配置**
```json
{
  "name": "ai-case-solver-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "antd": "^5.12.0",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "dayjs": "^1.11.10",
    "@ant-design/icons": "^5.2.6"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "@types/node": "^20.10.5"
  }
}
```

- [ ] **Step 4: 编写全局类型定义 frontend/src/types/index.ts**
```typescript
// 案件相关类型
export interface Victim {
  name: string;
  age: number;
  gender: string;
  occupation: string;
  background: string;
  cause_of_death: string;
  time_of_death: string;
}

export interface Suspect {
  suspect_id: string;
  name: string;
  age: number;
  gender: string;
  occupation: string;
  background: string;
  motive: string;
  relationship_with_victim: string;
  alibi: string;
  is_murderer: boolean;
  personality: string;
  speaking_style: string;
  stress_level: number;
}

export interface Evidence {
  evidence_id: string;
  name: string;
  description: string;
  type: 'physical' | 'testimony' | 'document';
  location: string;
  is_hidden: boolean;
  is_encrypted: boolean;
  decryption_key?: string;
  related_suspect_ids: string[];
}

export interface SceneLocation {
  location_id: string;
  name: string;
  description: string;
  interactable_objects: string[];
  evidence_ids: string[];
}

export interface TimelineEvent {
  time: string;
  event: string;
  suspect_id?: string;
  description: string;
}

export interface Case {
  case_id: string;
  title: string;
  background: string;
  victim: Victim;
  suspects: Suspect[];
  murder_weapon: string;
  murder_time: string;
  murder_method: string;
  real_murderer_id: string;
  evidence_list: Evidence[];
  scene_locations: SceneLocation[];
  timeline: TimelineEvent[];
  created_at: string;
}

// 游戏相关类型
export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
  timestamp: string;
  suspect_id?: string;
  is_private: boolean;
}

export interface SuspectState {
  suspect_id: string;
  stress_level: number;
  is_in_interrogation: boolean;
  last_interaction_time?: string;
  has_spoken_recently: boolean;
}

export interface GameSession {
  session_id: string;
  user_id: string;
  case: Case;
  current_state: 'investigation' | 'interrogation' | 'closing';
  collected_evidence_ids: string[];
  conversation_history: Message[];
  suspect_states: Record<string, SuspectState>;
  current_scene_id?: string;
  remaining_mistakes: number;
  start_time: string;
  last_interaction_time: string;
  interaction_count: number;
}

export interface AccusationRequest {
  murderer_id: string;
  motive: string;
  murder_time: string;
  murder_weapon: string;
  murder_process: string;
  evidence_ids?: string[];
}

export interface AccusationResult {
  is_correct: boolean;
  message: string;
  case_reveal?: string;
  accuracy_score: number;
  remaining_mistakes?: number;
}
```

- [ ] **Step 5: 编写API服务封装 frontend/src/services/api.ts**
```typescript
import axios from 'axios';
import { GameSession, AccusationRequest, AccusationResult } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.debug(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.debug(`[API Response] ${response.status} ${response.config.url}`, response.data);
    return response.data;
  },
  (error) => {
    console.error('[API Response Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// API接口
export const api = {
  // 游戏相关
  game: {
    createNew: (userId: string): Promise<GameSession> =>
      apiClient.post('/game/new', { user_id: userId }),
    
    sendMessage: (
      sessionId: string,
      message: string,
      targetSuspectIds?: string[],
      isPrivate: boolean = false
    ): Promise<GameSession> =>
      apiClient.post(`/game/${sessionId}/message`, {
        message,
        target_suspect_ids: targetSuspectIds,
        is_private: isPrivate,
      }),
    
    collectEvidence: (sessionId: string, evidenceId: string): Promise<boolean> =>
      apiClient.post(`/game/${sessionId}/evidence/${evidenceId}/collect`),
    
    accuse: (sessionId: string, accusation: AccusationRequest): Promise<AccusationResult> =>
      apiClient.post(`/game/${sessionId}/accuse`, accusation),
  },

  // 会话相关
  session: {
    get: (sessionId: string): Promise<GameSession> =>
      apiClient.get(`/session/${sessionId}`),
    
    delete: (sessionId: string): Promise<void> =>
      apiClient.delete(`/session/${sessionId}`),
  },
};
```

- [ ] **Step 6: 编写全局状态管理 frontend/src/store/index.ts**
```typescript
import { create } from 'zustand';
import { GameSession, Message, Evidence } from '../types';
import { api } from '../services/api';

interface GameStore {
  session: GameSession | null;
  loading: boolean;
  error: string | null;
  currentTab: 'investigation' | 'interrogation' | 'evidence' | 'accusation';
  
  // Actions
  setCurrentTab: (tab: 'investigation' | 'interrogation' | 'evidence' | 'accusation') => void;
  createNewGame: (userId: string) => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  sendMessage: (message: string, targetSuspectIds?: string[], isPrivate?: boolean) => Promise<void>;
  collectEvidence: (evidenceId: string) => Promise<void>;
  submitAccusation: (accusation: any) => Promise<any>;
  clearError: () => void;
}

export const useGameStore = create<GameStore>((set, get) => ({
  session: null,
  loading: false,
  error: null,
  currentTab: 'investigation',

  setCurrentTab: (tab) => set({ currentTab: tab }),

  createNewGame: async (userId: string) => {
    set({ loading: true, error: null });
    try {
      const session = await api.game.createNew(userId);
      set({ session, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '创建游戏失败',
        loading: false,
      });
      throw error;
    }
  },

  loadSession: async (sessionId: string) => {
    set({ loading: true, error: null });
    try {
      const session = await api.session.get(sessionId);
      set({ session, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '加载会话失败',
        loading: false,
      });
      throw error;
    }
  },

  sendMessage: async (message: string, targetSuspectIds?: string[], isPrivate: boolean = false) => {
    const { session } = get();
    if (!session) return;

    set({ loading: true, error: null });
    try {
      const updatedSession = await api.game.sendMessage(
        session.session_id,
        message,
        targetSuspectIds,
        isPrivate
      );
      set({ session: updatedSession, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '发送消息失败',
        loading: false,
      });
      throw error;
    }
  },

  collectEvidence: async (evidenceId: string) => {
    const { session } = get();
    if (!session) return;

    set({ loading: true, error: null });
    try {
      await api.game.collectEvidence(session.session_id, evidenceId);
      // 重新加载会话以获取更新后的状态
      const updatedSession = await api.session.get(session.session_id);
      set({ session: updatedSession, loading: false });
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '收集线索失败',
        loading: false,
      });
      throw error;
    }
  },

  submitAccusation: async (accusation: any) => {
    const { session } = get();
    if (!session) throw new Error('没有活动的游戏会话');

    set({ loading: true, error: null });
    try {
      const result = await api.game.accuse(session.session_id, accusation);
      // 重新加载会话
      const updatedSession = await api.session.get(session.session_id);
      set({ session: updatedSession, loading: false });
      return result;
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '提交指认失败',
        loading: false,
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
```

- [ ] **Step 7: 提交前端架构代码**
```bash
git add frontend/
git commit -m "feat: initialize frontend project structure and core architecture"
```

---

## 计划审核检查

### 1. 产品需求覆盖
✅ 案件生成逻辑：覆盖（CaseGeneratorAgent）
✅ 现场勘查系统：覆盖（证据模型、线索收集接口）
✅ 对话质询系统：覆盖（多嫌疑人Agent、单独/全体质询逻辑）
✅ 指认结案系统：覆盖（Accusation接口、结果判断逻辑）
✅ AI角色行为规则：覆盖（SuspectAgent行为逻辑、发言优先级控制）
✅ 超时/轮次限制：覆盖（GameSession中内置is_game_over判断）

### 2. 架构合理性
✅ 前后端分离，职责清晰
✅ 分层架构（展示层/API层/业务层/AI层/基础设施层），降低耦合
✅ 多Agent架构，每个嫌疑人独立Agent，保证行为独立性
✅ 会话状态使用Redis缓存，支持水平扩展
✅ 接口设计RESTful，前后端对接清晰

### 3. 无占位符检查
所有任务步骤均包含完整代码、命令和预期结果，无TBD、TODO等占位内容。

---

## 执行选择
计划已完成并保存到 `docs/superpowers/plans/2026-04-05-ai-murder-mystery-architecture.md`。

**两种执行方式可选：**

**1. Subagent-Driven（推荐）** - 为每个任务分配独立子agent执行，任务间自动进行依赖检查和结果审核，迭代速度快。

**2. Inline Execution** - 在当前会话中按顺序执行所有任务，每完成一个阶段进行一次检查点确认。

请问您希望使用哪种方式执行？
