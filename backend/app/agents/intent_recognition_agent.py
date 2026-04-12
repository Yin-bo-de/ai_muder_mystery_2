"""意图识别 Agent：结合对话历史理解用户提问意图"""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from enum import Enum

from app.core.config import settings
from app.models.agent import Message
from app.utils.logger import logger


# 定义自己的 UserIntent 枚举，避免循环导入
class UserIntent(str, Enum):
    """用户提问意图类型"""
    SINGLE = "single"  # 对一个人提问
    PARTIAL = "partial"  # 对部分人提问
    ALL = "all"  # 对所有人提问


class IntentRecognitionResult(BaseModel):
    """意图识别结果"""
    intent_type: UserIntent = Field(..., description="意图类型：对一个人提问(single) / 对部分人提问(partial) / 对所有人提问(all)")
    target_suspect_ids: List[str] = Field(..., description="目标嫌疑人ID列表")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度（0.0-1.0）")
    reasoning: str = Field(..., description="推理过程说明")


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
        """构建高质量的提示词模板"""
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

## 详细注意事项和示例场景

### 1. 追问场景
- 如果用户说"你呢？"、"那你说呢？"，通常是追问刚才被提问但没说话的人，或刚才说话的人
- 例如：用户问"张三，你昨晚在哪？"，李四回答后，用户说"你呢？"，通常是问张三

### 2. 指代消解场景
- 如果用户说"他"、"她"，需要结合上下文判断指代谁
- 例如：用户问"谁最后一个见到死者？"，张三回答"应该是李四"，用户说"他什么时候走的？"，这里"他"指李四

### 3. 对所有人提问场景
- 如果用户说"有人..."、"谁..."，通常是对所有人提问
- 例如："有人见过死者昨晚吗？"、"谁知道凶器在哪里？"

### 4. 明确提到名字场景
- 如果用户明确提到名字，直接对应该人
- 例如："李四，你和死者是什么关系？"

### 5. 对全体提问场景
- 如果用户说"大家"、"所有人"、"各位"，就是对所有人提问
- 例如："大家都说说自己的不在场证明"

### 6. 不确定时的处理
- 如果无法确定用户的意图，或上下文信息不足，返回对所有人提问（all）
- 例如："真的吗？"、"是吗？"、"怎么回事？"

## 输出格式要求
请严格按照以下格式输出：
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

        # 准备对话历史（使用配置的窗口大小）
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
