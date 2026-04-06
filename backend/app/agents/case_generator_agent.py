"""案件生成Agent：生成完整、逻辑自洽的案件数据"""
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough

from app.core.config import settings
from app.core.exceptions import CaseGenerateException
from app.models.case import Case, Victim, Suspect, Clue, EvidenceChain, Scene, EvidenceChainItem
from app.utils.logger import logger

class CaseGeneratorAgent:
    """案件生成Agent，负责生成完整的案件数据"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            # 关闭深度思考模式，加快响应速度
            model_kwargs={
                "reasoning_effort": "none",
                "response_format": {"type": "json_object"}
            }
        )
        self.parser = PydanticOutputParser(pydantic_object=Case)

        # 案件生成提示词模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一位专业的推理小说作家，擅长设计逻辑严谨、情节曲折的谋杀案谜题。
请生成一个完整的谋杀案件，包含所有必要的元素，逻辑必须自洽，没有明显的漏洞。

【核心要求】
1. 案件设定在现代都市背景，情节贴近现实，不要过于玄幻或离奇
2. 必须生成唯一的case_id字段，格式为"case_xxxxxx"，xxxxxx为6位随机数字
3. 死者身份合理，有明确的社会关系和死亡原因
4. 生成3-5个嫌疑人，每个人都有唯一的suspect_id，格式为"s1"、"s2"等，并且有合理的动机、时间线、不在场证明（可能有破绽），其中只有一个is_murderer=True
5. 真凶只有一个，作案手法合理，有明确的动机和完整的证据链
6. 线索分布合理：包含物证、证词、关联线索、解密线索，总数在10-15个之间，每个线索有唯一的clue_id，格式为"c1"、"c2"等，必须包含location、scene、description字段
7. 设计3个干扰性的剧情分支，增加推理难度
8. 所有人物性格鲜明，行为符合其人设
9. 案件难度中等，适合普通玩家在30-60分钟内破解

【必填字段清单】
以下字段必须完整存在，不能遗漏：
1. 顶层字段：
   - case_id: 字符串
   - title: 字符串
   - difficulty: 整数1-5
   - theme: 字符串
   - description: 字符串
   - victim: 完整的死者对象
   - suspects: 嫌疑人列表，3-5个
   - clues: 线索列表10-15个
   - scenes: 场景列表，每个场景有scene_id、name、description、items、is_crime_scene
   - evidence_chains: 证据链列表，包含完整的证据逻辑链
   - murderer_id: 真凶的嫌疑人ID，必须对应某个嫌疑人的suspect_id
   - murder_weapon: 明确的凶器描述
   - murder_motive: 真凶完整的作案动机
   - murder_method: 详细的作案手法描述
   - true_timeline: 真凶作案的完整真实时间线
   - red_herrings: 干扰线索列表

2. 每个线索必须包含：
   - clue_id
   - name
   - clue_type
   - status
   - description
   - location
   - scene
   - importance
   - related_suspects: 数组，不能为null，只能包含嫌疑人ID（s1, s2, s3等），**绝对不能包含死者ID（v开头的）**

{format_instructions}

【输出要求】
1. 严格按照指定的JSON格式输出，不要添加任何额外的说明文字、解释、思考过程
2. 确保所有字段都存在且格式正确，字段名严格匹配
3. JSON结构完整，没有语法错误，没有多余的逗号
4. 所有字符串内容中不要包含特殊字符，确保可以正常解析
5. 【强制要求】输出的JSON必须包含以下顶层字段，绝对不能遗漏：
   - scenes: 数组类型
   - evidence_chains: 数组类型
   - murderer_id: 字符串类型
   - murder_weapon: 字符串类型
   - murder_motive: 字符串类型
   - murder_method: 字符串类型
   - true_timeline: 对象类型
   - red_herrings: 数组类型

【最后检查】
⚠️ 输出前必须100%确认以下要求：
✅ 所有必填字段都已包含，**绝对不能遗漏scenes、evidence_chains、murderer_id、murder_weapon、murder_motive、murder_method、true_timeline、red_herrings这些顶层字段**
✅ 完整输出所有10-15条线索，不能只输出几条就结束
✅ JSON结构完整，闭合所有括号和引号，没有语法错误
✅ 字段名完全匹配要求，没有拼写错误
✅ 输出长度不受限制，完整输出所有内容，不要提前终止

【强制指令】
如果输出内容过长，**必须完整输出所有字段**，不要做任何截断，不要省略任何内容，直到整个JSON结构完全结束。
"""),
            ("human", "请生成一个完整的谋杀案件，确保逻辑严谨，证据链完整，所有必填字段都存在。"),
        ])

        # 构建LCEL链
        self.chain = (
            {"format_instructions": lambda _: self.parser.get_format_instructions()}
            | self.prompt
            | self.llm
            | self.parser
        )

    async def generate_case(self, difficulty: str = "medium") -> Case:
        """
        生成完整案件
        :param difficulty: 案件难度：easy/medium/hard，v1.0默认medium
        :return: Case对象，包含完整案件数据
        """
        try:
            logger.info("开始生成新案件...")

            # 调用LLM生成案件
            case = await self.chain.ainvoke({"difficulty": difficulty})
            logger.info(f"案件生成内容：{case}")

            # 自动补全缺失的ID，确保格式正确
            import random
            import string
            # 生成case_id如果不存在
            if not case.case_id:
                case.case_id = f"case_{''.join(random.choices(string.digits, k=6))}"

            # 生成嫌疑人ID如果不存在
            for i, suspect in enumerate(case.suspects):
                if not suspect.suspect_id:
                    suspect.suspect_id = f"s{i+1}"

            # 生成线索ID如果不存在
            for i, clue in enumerate(case.clues):
                if not clue.clue_id:
                    clue.clue_id = f"c{i+1}"

            # 校验案件完整性
            self._validate_case(case)

            logger.info(f"案件生成成功，案件ID: {case.case_id}，死者: {case.victim.name}，嫌疑人数量: {len(case.suspects)}")
            return case

        except Exception as e:
            # 用%格式化避免异常信息中的{}被当作占位符
            logger.error("案件生成失败: %s", str(e), exc_info=True)
            raise CaseGenerateException(f"案件生成失败: {str(e)}")

    def _validate_case(self, case: Case) -> None:
        """校验生成的案件是否完整合法"""
        errors = []

        # 检查必填字段
        if not case.case_id:
            errors.append("case_id不能为空")
        if not case.title:
            errors.append("案件标题不能为空")
        if not case.victim:
            errors.append("死者信息不能为空")
        if len(case.suspects) < 3 or len(case.suspects) > 5:
            errors.append(f"嫌疑人数量应为3-5个，当前为{len(case.suspects)}个")
        if not case.evidence_chains:
            errors.append("证据链不能为空")
        if len(case.clues) < 10 or len(case.clues) > 15:
            errors.append(f"线索数量应为10-15个，当前为{len(case.clues)}个")
        if not case.scenes:
            errors.append("场景信息不能为空")
        if not case.murderer_id:
            errors.append("真凶ID不能为空")

        # 检查真凶是否在嫌疑人列表中
        murderer_ids = [s.suspect_id for s in case.suspects if s.suspect_id == case.murderer_id]
        if not murderer_ids:
            errors.append(f"真凶ID {case.murderer_id} 不在嫌疑人列表中")

        # 检查所有线索关联的嫌疑人是否存在，自动过滤掉死者ID（v开头的）
        suspect_ids = [s.suspect_id for s in case.suspects]
        for clue in case.clues:
            # 过滤掉非嫌疑人ID（比如死者ID v001）
            clue.related_suspects = [rid for rid in clue.related_suspects if rid in suspect_ids]
            # 确保related_suspects不为空
            if not clue.related_suspects:
                # 如果过滤后为空，默认关联所有嫌疑人
                clue.related_suspects = suspect_ids.copy()

        if errors:
            raise CaseGenerateException(f"案件数据校验失败: {'; '.join(errors)}")

    def generate_case_sync(self, difficulty: str = "medium") -> Case:
        """同步生成案件，用于测试"""
        try:
            logger.info("开始同步生成新案件...")

            # 调用LLM生成案件
            case = self.chain.invoke({"difficulty": difficulty})

            # 自动补全缺失的ID，确保格式正确
            import random
            import string
            # 生成case_id如果不存在
            if not case.case_id:
                case.case_id = f"case_{''.join(random.choices(string.digits, k=6))}"

            # 生成嫌疑人ID如果不存在
            for i, suspect in enumerate(case.suspects):
                if not suspect.suspect_id:
                    suspect.suspect_id = f"s{i+1}"

            # 生成线索ID如果不存在
            for i, clue in enumerate(case.clues):
                if not clue.clue_id:
                    clue.clue_id = f"c{i+1}"

            # 校验案件完整性
            self._validate_case(case)

            logger.info(f"案件生成成功，案件ID: {case.case_id}，死者: {case.victim.name}")
            return case

        except Exception as e:
            # 用%格式化避免异常信息中的{}被当作占位符
            logger.error("案件生成失败: %s", str(e), exc_info=True)
            raise CaseGenerateException(f"案件生成失败: {str(e)}")

# 全局实例
case_generator = CaseGeneratorAgent()
