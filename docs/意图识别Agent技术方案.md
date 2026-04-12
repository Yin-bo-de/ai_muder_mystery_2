# 基于上下文的意图识别 Agent 技术方案

## 1. 问题背景

### 1.1 当前现状
- 现有实现：`dialogue_manager.py` 中的 `_analyze_user_intent()` 方法
- 实现方式：基于关键词规则匹配
- 功能限制：仅能识别明确的关键词（"大家"、"所有人"、嫌疑人名字等）

### 1.2 问题场景
在全体质询模式下，用户经常不会明确指定提问对象，需要结合对话历史理解意图：

**示例1：追问场景**
```
用户：张三，你昨晚在哪？
张三：我在商场购物。
用户：那你呢？  ← 需要理解是问其他人
```

**示例2：话题延续场景**
```
用户：有人见过死者昨晚吗？
李四：我没见过...
王五：我也没有。
用户：真的吗？  ← 需要理解是对刚才说话的人追问
```

**示例3：指代消解场景**
```
用户：谁最后一个见到死者？
张三：应该是李四，他们俩住隔壁。
用户：他什么时候走的？  ← 需要理解"他"指李四
```

**示例4：追问场景**
```
用户：张三，你昨晚在哪？
张三：我在商场购物。
用户：你和谁一起  ← 需要理解是问张三和谁一起购物
```
---

## 2. 技术方案设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│              DialogueManager                            │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  IntentRecognitionAgent (LLM)                   │  │
│  │     - 接收对话历史                                │  │
│  │     - 分析用户意图（所有场景都使用 Agent）        │  │
│  │     - 返回目标嫌疑人列表                          │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  结果验证                                         │  │
│  │     - 验证嫌疑人ID有效性                          │  │
│  │     - 失败时回退到规则（兜底）                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

#### 2.2.1 IntentRecognitionAgent 类

**位置**：`backend/app/agents/intent_recognition_agent.py`

**核心职责**：
- 结合对话历史分析用户提问意图
- 识别目标嫌疑人列表
- 输出意图类型和置信度

**数据结构**：
```python
class IntentRecognitionResult(BaseModel):
    """意图识别结果"""
    intent_type: UserIntent  # SINGLE / PARTIAL / ALL
    target_suspect_ids: List[str]  # 目标嫌疑人ID列表
    confidence: float  # 置信度 0.0-1.0
    reasoning: str  # 推理过程说明（调试用）
```

#### 2.2.2 Agent 工作流

```python
async def analyze_intent_with_context(
    self,
    message: str,
    dialogue_history: List[Message],
    suspect_names: Dict[str, str],  # id -> name
) -> Tuple[UserIntent, List[str]]:
    """
    使用 IntentRecognitionAgent 进行意图识别
    """
    # 直接调用 LLM Agent
    llm_result = await self.intent_agent.analyze(
        message=message,
        dialogue_history=dialogue_history,
        suspect_names=suspect_names
    )

    # 验证结果
    return self._validate_result(llm_result)
```

---

## 3. 详细实现设计

### 3.1 IntentRecognitionAgent 实现

**文件**：`backend/app/agents/intent_recognition_agent.py`

```python
"""意图识别 Agent：结合对话历史理解用户提问意图"""
from typing import List, Dict, Tuple, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import settings
from app.models.agent import Message
from app.agents.dialogue_manager import UserIntent
from app.utils.logger import logger


class IntentRecognitionResult(BaseModel):
    """意图识别结果"""
    intent_type: UserIntent
    target_suspect_ids: List[str]
    confidence: float
    reasoning: str


class IntentRecognitionAgent:
    """意图识别 Agent"""

    def __init__(self, suspect_id_to_name: Dict[str, str]):
        """
        初始化意图识别 Agent
        :param suspect_id_to_name: 嫌疑人ID到名字的映射
        """
        self.suspect_id_to_name = suspect_id_to_name
        self.suspect_name_to_id = {
            name: sid for sid, name in suspect_id_to_name.items()
        }

        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # 低温度，保证确定性
            max_tokens=500,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

        # 输出解析器
        self.output_parser = PydanticOutputParser(
            pydantic_object=IntentRecognitionResult
        )

        # 构建提示词
        self.prompt = self._build_prompt()
        self.chain = self.prompt | self.llm | self.output_parser

    def _build_prompt(self) -> ChatPromptTemplate:
        """构建提示词模板"""
        template = """你是一个专业的对话意图分析助手，负责在谋杀案调查的全体质询场景中，
分析侦探（用户）的提问意图，确定问题是针对谁的。

## 嫌疑人列表
{suspects_list}

## 对话历史（最近30轮）
{dialogue_history}

## 当前问题
用户最新提问："{user_message}"

## 任务
请分析用户的提问意图，判断：
1. intent_type: 对一个人提问(single) / 对部分人提问(partial) / 对所有人提问(all)
2. target_suspect_ids: 目标嫌疑人ID列表（从上面的嫌疑人列表中选择）
3. confidence: 你的置信度（0.0-1.0）
4. reasoning: 简短说明你的推理过程

## 注意事项
- 如果用户说"你呢？"、"那你说呢？"，通常是追问刚才被提问但没说话的人，或刚才说话的人
- 如果用户说"他"、"她"，需要结合上下文判断指代谁
- 如果用户说"有人..."、"谁..."，通常是对所有人提问
- 如果用户明确提到名字，直接对应该人
- 如果用户说"大家"、"所有人"、"各位"，就是对所有人提问
- 如果不确定，返回对所有人提问（all）

{format_instructions}
"""

        return ChatPromptTemplate.from_messages([
            ("system", template),
        ])

    async def analyze(
        self,
        message: str,
        dialogue_history: List[Message],
    ) -> IntentRecognitionResult:
        """
        分析用户意图
        :param message: 当前用户消息
        :param dialogue_history: 对话历史（按时间顺序，最新的在最后）
        :return: 意图识别结果
        """
        # 准备嫌疑人列表
        suspects_list = "\n".join([
            f"- ID: {sid}, 姓名: {name}"
            for sid, name in self.suspect_id_to_name.items()
        ])

        # 准备对话历史（最近30轮）
        recent_history = dialogue_history[-settings.INTENT_RECOGNITION_HISTORY_WINDOW:] \
            if len(dialogue_history) > settings.INTENT_RECOGNITION_HISTORY_WINDOW \
            else dialogue_history
        history_text = "\n".join([
            f"[{msg.timestamp.strftime('%H:%M:%S')}] {msg.sender_name}: {msg.content}"
            for msg in recent_history
        ])

        try:
            # 调用 LLM
            result = await self.chain.ainvoke({
                "suspects_list": suspects_list,
                "dialogue_history": history_text,
                "user_message": message,
                "format_instructions": self.output_parser.get_format_instructions(),
            })

            logger.info(f"意图识别成功: intent={result.intent_type}, "
                       f"targets={result.target_suspect_ids}, "
                       f"confidence={result.confidence}")
            return result

        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            # 失败时返回对所有人提问
            return IntentRecognitionResult(
                intent_type=UserIntent.ALL,
                target_suspect_ids=list(self.suspect_id_to_name.keys()),
                confidence=0.0,
                reasoning=f"LLM调用失败: {str(e)}",
            )
```

### 3.2 DialogueManager 集成

**修改位置**：`backend/app/agents/dialogue_manager.py`

**主要变更**：
1. 初始化时创建 `IntentRecognitionAgent` 实例
2. 修改 `_analyze_user_intent()` 为调用 Agent
3. 保留原有规则方法作为兜底
4. 新增 `_validate_result()` 结果验证方法

```python
class DialogueManager:
    def __init__(self, suspects: List[Suspect], true_murderer_id: str, case: Optional[Case] = None):
        # ... 现有代码 ...

        # 新增：意图识别 Agent
        self.intent_recognition_agent: Optional[IntentRecognitionAgent] = None
        if settings.ENABLE_INTENT_RECOGNITION_AGENT:
            self.intent_recognition_agent = IntentRecognitionAgent(
                suspect_id_to_name=self.suspect_names
            )
            logger.info("意图识别 Agent 已启用")

    async def _analyze_user_intent_with_context(
        self,
        message: str,
        dialogue_history: List[Message],
    ) -> Tuple[UserIntent, List[str]]:
        """
        结合上下文分析用户意图（使用 IntentRecognitionAgent）
        """
        # 如果 Agent 未启用，回退到规则
        if not self.intent_recognition_agent:
            return self._analyze_user_intent(message)

        try:
            # 调用意图识别 Agent
            logger.info(f"调用意图识别 Agent: {message}")
            llm_result = await self.intent_recognition_agent.analyze(
                message=message,
                dialogue_history=dialogue_history,
            )

            # 验证结果
            return self._validate_result(llm_result)

        except Exception as e:
            logger.error(f"意图识别 Agent 调用失败，回退到规则: {e}")
            # 失败时回退到规则
            return self._analyze_user_intent(message)

    def _validate_result(
        self,
        llm_result: IntentRecognitionResult,
    ) -> Tuple[UserIntent, List[str]]:
        """
        验证意图识别结果
        """
        # 验证嫌疑人ID是否有效
        valid_targets = [
            sid for sid in llm_result.target_suspect_ids
            if sid in self.suspect_agents
        ]

        if not valid_targets:
            logger.warning(f"LLM 返回的目标嫌疑人无效，回退到所有人: {llm_result.target_suspect_ids}")
            return UserIntent.ALL, list(self.suspect_agents.keys())

        # 使用 LLM 的结果
        logger.info(f"使用意图识别结果: {llm_result.intent_type}, {valid_targets}")
        return llm_result.intent_type, valid_targets
```

### 3.3 配置项

**文件**：`backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # ... 现有配置 ...

    # 意图识别 Agent 配置
    ENABLE_INTENT_RECOGNITION_AGENT: bool = Field(
        default=True,
        description="是否启用基于 LLM 的意图识别 Agent"
    )
    INTENT_RECOGNITION_HISTORY_WINDOW: int = Field(
        default=30,
        description="意图识别使用的对话历史窗口大小"
    )
```

---

## 4. 集成与迁移

### 4.1 修改的文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `backend/app/agents/intent_recognition_agent.py` | 新建 | 新增意图识别 Agent |
| `backend/app/agents/dialogue_manager.py` | 修改 | 集成意图识别 Agent |
| `backend/app/core/config.py` | 修改 | 添加配置项 |
| `backend/tests/unit/test_intent_recognition_agent.py` | 新建 | 单元测试 |

### 4.2 向后兼容性

- 默认启用，但可以通过配置关闭
- LLM 失败时自动回退到规则
- 不影响现有 API 接口

---

## 5. 测试策略

### 5.1 单元测试
- 测试 LLM 意图识别（Mock LLM）
- 测试结果验证逻辑
- 测试回退策略

### 5.2 集成测试
- 测试完整对话流程
- 测试典型场景（追问、指代消解等）

### 5.3 E2E 测试
- 测试真实游戏场景中的意图识别

---

## 6. 性能考虑

### 6.1 成本
- 每次用户消息都调用 LLM
- 预期 LLM 调用率：100%

### 6.2 响应时间
- LLM 路径：500-2000ms（取决于模型）

### 6.3 缓存策略
- 相同消息 + 相同历史 = 缓存结果
- 缓存大小：最近 100 次请求

---

## 7. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| LLM 识别错误 | 中 | 中 | 验证逻辑 + 规则回退 |
| 响应时间增加 | 中 | 高 | 可配置开关，用户可选择 |
| Token 成本增加 | 低 | 中 | 限制历史窗口大小 |
| 配置关闭后功能降级 | 低 | 低 | 规则作为兜底，功能可用 |

---

## 8. 后续优化方向

### 8.1 短期
- 添加意图识别效果的日志分析
- 收集误识别案例，优化提示词
- 添加用户反馈机制（用户可修正意图）

### 8.2 中期
- 训练专用的小模型（成本更低、速度更快）
- 添加意图识别的 A/B 测试框架
- 支持多语言意图识别

### 8.3 长期
- 结合用户行为模式个性化意图识别
- 实时学习和适应用户提问习惯
