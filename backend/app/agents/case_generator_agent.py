"""案件生成Agent：生成完整、逻辑自洽的案件数据"""
import json
import random
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.core.config import settings
from app.core.constants import ClueType, ContradictionType, ClueStatus
from app.core.exceptions import CaseGenerateException
from app.models.case import Case, Victim, Suspect, Clue, EvidenceChain, Scene, EvidenceChainItem, ContradictionPoint
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
请输出JSON格式的数据。

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

【嫌疑人增强字段要求】
为每个嫌疑人添加以下字段：
1. refusal_threshold: 0.3-0.8之间的浮点数，表示嫌疑人的反驳阈值，值越低越容易反驳
2. counter_evidence: 字符串数组，包含1-3条可以用来反驳他人的证据内容
3. personality_modifier: 0.5-1.5之间的浮点数，表示人设修正系数（冲动型>1.0，冷静型<1.0）
4. spatial_relationships: 对象，键是其他嫌疑人ID，值是"positive"（关系好）、"negative"（关系差）、"neutral"（一般）

【矛盾点设计要求】
设计2-4个嫌疑人之间的矛盾点（contradiction_points）：
1. 时间线矛盾：两个嫌疑人对同一时间段的描述不一致
2. 空间矛盾：两个嫌疑人声称在同一地点但没有看到对方
3. 证据矛盾：某个嫌疑人的陈述与物证不符

每个矛盾点包含：
- contradiction_id: 格式"cp1"、"cp2"等
- contradiction_type: "timeline"（时间线）、"spatial"（空间）、"evidence"（证据）
- description: 矛盾点的详细描述
- involved_suspects: 涉及的嫌疑人ID数组
- trigger_keywords: 触发关键词数组，当用户提到这些词时可能触发矛盾检测
- requires_both_speaking: 是否需要两个嫌疑人都发言过才触发
- refuting_suspect: 主动反驳的嫌疑人ID
- refutation_target: 被反驳的嫌疑人ID

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
   - clue_type: 只能是以下值之一：physical（物证）、testimony（证词）、association（关联线索）、decrypt（需解密线索）、document（文档类线索）
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
✅ 所有线索的clue_type只能是physical、testimony、association、decrypt、document中的一个
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

            # 生成线索ID如果不存在，并修复clue_type
            for i, clue in enumerate(case.clues):
                if not clue.clue_id:
                    clue.clue_id = f"c{i+1}"
                # 修复不合法的clue_type
                clue.clue_type = self._fix_clue_type(clue.clue_type)
                # 确保所有线索的初始状态都是 HIDDEN
                clue.status = ClueStatus.HIDDEN

            # 校验案件完整性
            self._validate_case(case)

            # 自动补充矛盾点和嫌疑人增强字段（如果LLM没有生成）
            self._enhance_case_with_contradictions(case)

            logger.info(f"案件生成成功，案件ID: {case.case_id}，死者: {case.victim.name}，嫌疑人数量: {len(case.suspects)}，矛盾点数量: {len(case.contradiction_points or [])}")
            return case

        except Exception as e:
            # 用%格式化避免异常信息中的{}被当作占位符
            logger.error("案件生成失败: %s", str(e), exc_info=True)
            raise CaseGenerateException(f"案件生成失败: {str(e)}")

    def _enhance_case_with_contradictions(self, case: Case) -> None:
        """
        自动增强案件，添加矛盾点和嫌疑人增强字段（如果LLM没有生成）
        :param case: 案件对象
        """
        # 1. 为嫌疑人添加增强字段
        self._add_suspect_enhancements(case)

        # 2. 生成矛盾点
        if not case.contradiction_points or len(case.contradiction_points) == 0:
            case.contradiction_points = self._generate_contradiction_points(case)

        # 3. 添加矛盾线索
        self._add_contradiction_clues(case)

    def _add_suspect_enhancements(self, case: Case) -> None:
        """
        为嫌疑人添加增强字段
        :param case: 案件对象
        """
        suspect_ids = [s.suspect_id for s in case.suspects]

        for suspect in case.suspects:
            # 1. 添加refusal_threshold（0.3-0.8之间）
            if not hasattr(suspect, 'refusal_threshold') or suspect.refusal_threshold is None:
                # 真凶的反驳阈值更低（更容易反驳）
                if suspect.is_murderer:
                    suspect.refusal_threshold = random.uniform(0.3, 0.5)
                else:
                    suspect.refusal_threshold = random.uniform(0.5, 0.8)

            # 2. 添加personality_modifier（0.5-1.5之间）
            if not hasattr(suspect, 'personality_modifier') or suspect.personality_modifier is None:
                # 根据性格描述判断
                personality_lower = suspect.personality_traits if suspect.personality_traits else ""
                if any(keyword in personality_lower for keyword in ['暴躁', '冲动', '易怒', '急躁']):
                    suspect.personality_modifier = random.uniform(1.2, 1.5)
                elif any(keyword in personality_lower for keyword in ['冷静', '沉稳', '内向', '谨慎']):
                    suspect.personality_modifier = random.uniform(0.5, 0.8)
                else:
                    suspect.personality_modifier = random.uniform(0.9, 1.1)

            # 3. 添加counter_evidence
            if not hasattr(suspect, 'counter_evidence') or suspect.counter_evidence is None:
                suspect.counter_evidence = self._generate_counter_evidence(suspect, case.suspects)

            # 4. 添加spatial_relationships
            if not hasattr(suspect, 'spatial_relationships') or suspect.spatial_relationships is None:
                suspect.spatial_relationships = {}
                for other_id in suspect_ids:
                    if other_id != suspect.suspect_id:
                        # 随机生成关系，真凶和被嫁祸者关系设为negative
                        other_suspect = next((s for s in case.suspects if s.suspect_id == other_id), None)
                        if other_suspect:
                            if suspect.is_murderer and other_suspect.motive and not other_suspect.is_murderer:
                                # 真凶对有动机的嫌疑人关系差（准备嫁祸）
                                suspect.spatial_relationships[other_id] = "negative"
                            elif other_suspect.is_murderer and suspect.motive and not suspect.is_murderer:
                                # 被嫁祸者对真凶关系差
                                suspect.spatial_relationships[other_id] = "negative"
                            else:
                                # 随机关系
                                suspect.spatial_relationships[other_id] = random.choice(["positive", "negative", "neutral"])

    def _generate_counter_evidence(self, suspect: Suspect, all_suspects: List[Suspect]) -> List[str]:
        """
        为嫌疑人生成反驳证据
        :param suspect: 嫌疑人对象
        :param all_suspects: 所有嫌疑人列表
        :return: 反驳证据列表
        """
        evidences = []

        # 生成1-3条反驳证据
        num_evidences = random.randint(1, 3)

        # 基于不在场证明生成反驳
        if suspect.alibi:
            evidences.append(f"我有不在场证明：{suspect.alibi}")

        # 基于关系生成反驳
        if suspect.relationship_with_victim:
            if "好" in suspect.relationship_with_victim or "朋友" in suspect.relationship_with_victim:
                evidences.append(f"我和死者关系一直很好，没有理由害他")

        # 基于性格生成反驳
        if suspect.personality_traits:
            if "内向" in suspect.personality_traits or "懦弱" in suspect.personality_traits:
                evidences.append("我这个人胆子很小，根本不敢做这种事")

        # 补充通用反驳
        general_evidences = [
            "案发时我根本不在现场",
            "你们没有证据证明是我干的",
            "我是被冤枉的，有人想嫁祸给我",
            "我真的什么都不知道",
        ]

        # 补充不足的
        while len(evidences) < num_evidences:
            evidence = random.choice(general_evidences)
            if evidence not in evidences:
                evidences.append(evidence)

        return evidences[:num_evidences]

    def _generate_contradiction_points(self, case: Case) -> List[ContradictionPoint]:
        """
        自动生成矛盾点
        :param case: 案件对象
        :return: 矛盾点列表
        """
        contradiction_points = []
        suspect_ids = [s.suspect_id for s in case.suspects]

        if len(suspect_ids) < 2:
            return contradiction_points

        # 生成2-4个矛盾点
        num_contradictions = random.randint(2, 4)

        # 1. 时间线矛盾（必有）
        if num_contradictions >= 1:
            timeline_contradiction = self._create_timeline_contradiction(case, suspect_ids)
            if timeline_contradiction:
                contradiction_points.append(timeline_contradiction)

        # 2. 空间矛盾（可选）
        if num_contradictions >= 2 and len(suspect_ids) >= 2:
            spatial_contradiction = self._create_spatial_contradiction(case, suspect_ids)
            if spatial_contradiction:
                contradiction_points.append(spatial_contradiction)

        # 3. 证据矛盾（可选）
        if num_contradictions >= 3:
            evidence_contradiction = self._create_evidence_contradiction(case, suspect_ids)
            if evidence_contradiction:
                contradiction_points.append(evidence_contradiction)

        return contradiction_points

    def _create_timeline_contradiction(self, case: Case, suspect_ids: List[str]) -> Optional[ContradictionPoint]:
        """创建时间线矛盾"""
        if len(suspect_ids) < 2:
            return None

        # 选择两个嫌疑人
        s1, s2 = random.sample(suspect_ids, 2)
        s1_name = next((s.name for s in case.suspects if s.suspect_id == s1), "嫌疑人A")
        s2_name = next((s.name for s in case.suspects if s.suspect_id == s2), "嫌疑人B")

        # 选择反驳方和被反驳方（真凶更可能成为反驳方）
        s1_is_murderer = next((s.is_murderer for s in case.suspects if s.suspect_id == s1), False)
        s2_is_murderer = next((s.is_murderer for s in case.suspects if s.suspect_id == s2), False)

        if s1_is_murderer and not s2_is_murderer:
            refuting, refuted = s1, s2
            refuting_name, refuted_name = s1_name, s2_name
        elif s2_is_murderer and not s1_is_murderer:
            refuting, refuted = s2, s1
            refuting_name, refuted_name = s2_name, s1_name
        else:
            refuting, refuted = s1, s2
            refuting_name, refuted_name = s1_name, s2_name

        time_slots = ["晚上8点", "晚上9点", "晚上10点", "凌晨12点", "下午3点"]
        selected_time = random.choice(time_slots)

        return ContradictionPoint(
            contradiction_id=f"cp{len([p for p in case.contradiction_points if p]) + 1}",
            contradiction_type=ContradictionType.TIMELINE,
            description=f"{refuting_name}声称{selected_time}在现场附近看到了{refuted_name}，但{refuted_name}说当时自己在别的地方",
            involved_suspects=[refuting, refuted],
            trigger_keywords=[selected_time, "看到", "时间", "在哪里", "几点"],
            requires_both_speaking=True,
            refuting_suspect=refuting,
            refutation_target=refuted
        )

    def _create_spatial_contradiction(self, case: Case, suspect_ids: List[str]) -> Optional[ContradictionPoint]:
        """创建空间矛盾"""
        if len(suspect_ids) < 2:
            return None

        s1, s2 = random.sample(suspect_ids, 2)
        s1_name = next((s.name for s in case.suspects if s.suspect_id == s1), "嫌疑人A")
        s2_name = next((s.name for s in case.suspects if s.suspect_id == s2), "嫌疑人B")

        locations = ["死者家门口", "小区便利店", "停车场", "咖啡馆", "楼下花园"]
        location = random.choice(locations)

        return ContradictionPoint(
            contradiction_id=f"cp{len([p for p in case.contradiction_points if p]) + 2}",
            contradiction_type=ContradictionType.SPATIAL,
            description=f"{s1_name}和{s2_name}都声称{location}待过一段时间，但两人都说没有看到对方",
            involved_suspects=[s1, s2],
            trigger_keywords=[location, "在那里", "碰到", "遇见"],
            requires_both_speaking=True,
            refuting_suspect=s1,
            refutation_target=s2
        )

    def _create_evidence_contradiction(self, case: Case, suspect_ids: List[str]) -> Optional[ContradictionPoint]:
        """创建证据矛盾"""
        if len(suspect_ids) < 1:
            return None

        s1 = random.choice(suspect_ids)
        s1_name = next((s.name for s in case.suspects if s.suspect_id == s1), "嫌疑人A")

        evidence_types = ["指纹", "脚印", "DNA", "监控录像", "手机记录"]
        evidence = random.choice(evidence_types)

        return ContradictionPoint(
            contradiction_id=f"cp{len([p for p in case.contradiction_points if p]) + 3}",
            contradiction_type=ContradictionType.EVIDENCE,
            description=f"现场发现了{s1_name}的{evidence}，但{s1_name}坚持说自己从来没有去过现场",
            involved_suspects=[s1],
            trigger_keywords=[evidence, "现场", "痕迹", "怎么解释"],
            requires_both_speaking=False,
            refuting_suspect=s1,
            refutation_target=None
        )

    def _add_contradiction_clues(self, case: Case) -> None:
        """
        添加与矛盾点相关的线索
        :param case: 案件对象
        """
        if not case.contradiction_points or len(case.contradiction_points) == 0:
            return

        # 现有的线索ID
        existing_clue_ids = [c.clue_id for c in case.clues]
        next_clue_num = len(existing_clue_ids) + 1

        for cp in case.contradiction_points:
            # 为每个矛盾点添加1-2条线索
            num_clues = random.randint(1, 2)
            for _ in range(num_clues):
                clue_id = f"c{next_clue_num}"
                while clue_id in existing_clue_ids:
                    next_clue_num += 1
                    clue_id = f"c{next_clue_num}"

                # 生成线索
                clue = self._create_contradiction_clue(clue_id, cp, case)
                if clue:
                    case.clues.append(clue)
                    existing_clue_ids.append(clue_id)
                    next_clue_num += 1

    def _create_contradiction_clue(self, clue_id: str, cp: ContradictionPoint, case: Case) -> Optional[Clue]:
        """创建矛盾线索"""
        if cp.contradiction_type == ContradictionType.TIMELINE:
            return Clue(
                clue_id=clue_id,
                name="模糊的时间记录",
                clue_type=ClueType.DOCUMENT,
                status=ClueStatus.HIDDEN,
                description=f"一份损坏的监控记录，似乎能证明某些人的时间线有问题",
                location="保安室",
                scene=case.scenes[0].scene_id if case.scenes else "s1",
                importance=0.9,
                related_suspects=cp.involved_suspects
            )
        elif cp.contradiction_type == ContradictionType.SPATIAL:
            return Clue(
                clue_id=clue_id,
                name="路人的证词",
                clue_type=ClueType.TESTIMONY,
                status=ClueStatus.HIDDEN,
                description="一位路人说好像看到了什么，但记不太清了",
                location="小区门口",
                scene=case.scenes[0].scene_id if case.scenes else "s1",
                importance=0.7,
                related_suspects=cp.involved_suspects
            )
        elif cp.contradiction_type == ContradictionType.EVIDENCE:
            return Clue(
                clue_id=clue_id,
                name="补充鉴定报告",
                clue_type=ClueType.DOCUMENT,
                status=ClueStatus.HIDDEN,
                description="一份详细的鉴定报告，可能揭示更多细节",
                location="法医室",
                scene=case.scenes[0].scene_id if case.scenes else "s1",
                importance=0.95,
                related_suspects=cp.involved_suspects
            )
        return None

    def _fix_clue_type(self, clue_type: str) -> ClueType:
        """
        修复不合法的clue_type，确保兼容性
        :param clue_type: 原始clue_type字符串
        :return: 合法的ClueType枚举值
        """
        # 合法的clue_type映射
        type_mapping = {
            "physical": ClueType.PHYSICAL,
            "physcial": ClueType.PHYSICAL,  # 常见拼写错误
            "testimony": ClueType.TESTIMONY,
            "association": ClueType.ASSOCIATION,
            "decrypt": ClueType.DECRYPT,
            "document": ClueType.DOCUMENT,
            "doc": ClueType.DOCUMENT,
            "paper": ClueType.DOCUMENT,
            "note": ClueType.DOCUMENT,
            "letter": ClueType.DOCUMENT,
        }

        # 如果已经是合法的枚举值，直接返回
        if isinstance(clue_type, ClueType):
            return clue_type

        # 尝试转换字符串
        clue_type_lower = str(clue_type).lower()
        if clue_type_lower in type_mapping:
            return type_mapping[clue_type_lower]

        # 默认返回physical作为兜底
        logger.warning(f"未知的clue_type: {clue_type}，已默认转换为physical")
        return ClueType.PHYSICAL

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
            # 再次确保clue_type是合法的
            clue.clue_type = self._fix_clue_type(clue.clue_type)

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

            # 生成线索ID如果不存在，并修复clue_type
            for i, clue in enumerate(case.clues):
                if not clue.clue_id:
                    clue.clue_id = f"c{i+1}"
                # 修复不合法的clue_type
                clue.clue_type = self._fix_clue_type(clue.clue_type)
                # 确保所有线索的初始状态都是 HIDDEN
                clue.status = ClueStatus.HIDDEN

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
