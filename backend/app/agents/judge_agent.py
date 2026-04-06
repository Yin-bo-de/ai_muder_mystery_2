"""裁判Agent：结案阶段处理、案件正确性判断、复盘报告生成"""
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import AccusationInvalidException
from app.models.case import Case, Clue
from app.models.game import GameSession
from app.utils.logger import logger

class JudgeAgent:
    """裁判Agent，负责判断指认正确性和生成结案报告"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.3,  # 裁判需要严谨，温度低
            max_tokens=1000,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            # 关闭深度思考模式，加快响应速度
            model_kwargs={
                "reasoning_effort": "none",
                "response_format": {"type": "json_object"}
            }
        )

        # 结案报告模板
        self.report_prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一位专业的侦探裁判，负责评估玩家的破案过程和判断指认是否正确。

案件信息：
案件标题：{case_title}
死者：{victim_name}
真凶：{murderer_name}
作案动机：{murderer_motive}
作案手法：{murderer_modus_operandi}
完整证据链：{evidence_chain}

玩家指认信息：
指认的嫌疑人：{accused_name}
玩家陈述的动机：{player_motive}
玩家陈述的作案手法：{player_modus_operandi}
玩家提供的证据：{player_evidence}
玩家收集线索完成度：{clue_completion_rate}%

请根据以上信息，完成以下任务：
1. 判断玩家的指认是否正确
2. 评估玩家的推理准确率（0-100分）
3. 生成详细的结案报告，包含：
   - 案件真相还原
   - 玩家推理的亮点和遗漏点
   - 关键证据分析
   - 探案过程评价

请用中文回复，语言流畅，逻辑清晰，符合侦探小说的叙事风格。
"""),
            ("human", "请生成结案报告和评估结果。"),
        ])

    async def judge_accusation(
        self,
        session: GameSession,
        accused_suspect_id: str,
        player_motive: str,
        player_modus_operandi: str,
        player_evidence: List[str],
    ) -> Dict[str, Any]:
        """
        判断玩家指认是否正确，生成结案报告
        :param session: 游戏会话对象
        :param accused_suspect_id: 玩家指认的嫌疑人ID
        :param player_motive: 玩家陈述的动机
        :param player_modus_operandi: 玩家陈述的作案手法
        :param player_evidence: 玩家提供的证据ID列表
        :return: 裁判结果
        """
        try:
            case = session.case
            logger.info(f"开始裁判指认，案件: {case.case_id}，玩家指认: {accused_suspect_id}，真凶: {case.murderer_id}")

            # 基础正确性判断
            is_correct = accused_suspect_id == case.murderer_id

            # 计算线索完成率
            clue_completion_rate = int((len(session.collected_clues) / len(case.clues)) * 100)

            # 查找真凶信息
            true_murderer = next(
                (s for s in case.suspects if s.suspect_id == case.murderer_id),
                None
            )
            accused_suspect = next(
                (s for s in case.suspects if s.suspect_id == accused_suspect_id),
                None
            )

            if not accused_suspect:
                raise AccusationInvalidException(f"无效的嫌疑人ID: {accused_suspect_id}")

            # 计算证据匹配度（合并所有证据链的required_clues作为关键证据）
            key_evidence_ids = []
            for chain in case.evidence_chains:
                key_evidence_ids.extend(chain.required_clues)
            key_evidence_ids = list(set(key_evidence_ids))  # 去重

            evidence_match_score = self._calculate_evidence_match_score(
                player_evidence,
                key_evidence_ids,
                session.collected_clues
            )

            # 计算推理准确率
            accuracy_score = self._calculate_accuracy_score(
                is_correct,
                clue_completion_rate,
                evidence_match_score,
                player_motive,
                player_modus_operandi,
                true_murderer
            )

            # 生成结案报告
            report = await self._generate_final_report(
                case=case,
                true_murderer=true_murderer,
                accused_suspect=accused_suspect,
                is_correct=is_correct,
                player_motive=player_motive,
                player_modus_operandi=player_modus_operandi,
                player_evidence=player_evidence,
                clue_completion_rate=clue_completion_rate,
                accuracy_score=accuracy_score,
            )

            # 生成探案复盘
            review = self._generate_case_review(
                session=session,
                is_correct=is_correct,
                accuracy_score=accuracy_score,
                clue_completion_rate=clue_completion_rate,
            )

            logger.info(f"指认裁判完成，结果: {'正确' if is_correct else '错误'}, 准确率: {accuracy_score}分")

            return {
                "is_correct": is_correct,
                "accuracy_score": accuracy_score,
                "clue_completion_rate": clue_completion_rate,
                "evidence_match_score": evidence_match_score,
                "report": report,
                "review": review,
                "true_murderer_id": case.murderer_id,
                "true_murderer_name": true_murderer.name if true_murderer else "",
            }

        except Exception as e:
            logger.error(f"裁判指认失败: {str(e)}", exc_info=True)
            raise AccusationInvalidException(f"裁判失败: {str(e)}")

    def _calculate_evidence_match_score(
        self,
        player_evidence: List[str],
        key_evidence_ids: List[str],
        collected_clues: List[Clue],
    ) -> int:
        """计算证据匹配得分（0-100）"""
        if not key_evidence_ids:
            return 100

        # 计算玩家提供的证据中有多少是关键证据
        matched_key_evidence = [e for e in player_evidence if e in key_evidence_ids]
        key_evidence_ratio = len(matched_key_evidence) / len(key_evidence_ids) if key_evidence_ids else 1

        # 计算证据完整度
        collected_key_evidence = [c.clue_id for c in collected_clues if c.clue_id in key_evidence_ids]
        collection_ratio = len(collected_key_evidence) / len(key_evidence_ids) if key_evidence_ids else 1

        return int((key_evidence_ratio * 0.7 + collection_ratio * 0.3) * 100)

    def _calculate_accuracy_score(
        self,
        is_correct: bool,
        clue_completion_rate: int,
        evidence_match_score: int,
        player_motive: str,
        player_modus_operandi: str,
        true_murderer: Any,
    ) -> int:
        """计算推理准确率得分（0-100）"""
        if not is_correct:
            # 指认错误最多得50分
            base_score = 30
            return min(50, base_score + int(clue_completion_rate * 0.2))

        # 指认正确的情况下计算得分
        base_score = 60

        # 线索完成度加分（最多20分）
        base_score += int(clue_completion_rate * 0.2)

        # 证据匹配度加分（最多15分）
        base_score += int(evidence_match_score * 0.15)

        # 动机描述匹配加分（最多5分）
        if true_murderer and true_murderer.motive in player_motive:
            base_score += 5

        return min(100, base_score)

    async def _generate_final_report(
        self,
        case: Case,
        true_murderer: Any,
        accused_suspect: Any,
        is_correct: bool,
        player_motive: str,
        player_modus_operandi: str,
        player_evidence: List[str],
        clue_completion_rate: int,
        accuracy_score: int,
    ) -> Dict[str, Any]:
        """生成最终结案报告"""
        # v1.0 简化实现，直接返回结构化报告
        if is_correct:
            result_title = "🎉 指认正确！案件告破！"
            result_description = f"恭喜你成功找出了真凶 {true_murderer.name}！"
        else:
            result_title = "❌ 指认错误！"
            result_description = f"很遗憾，你指认的 {accused_suspect.name} 不是真凶。真正的凶手是 {true_murderer.name}。"

        return {
            "title": result_title,
            "description": result_description,
            "accuracy_score": accuracy_score,
            "clue_completion_rate": clue_completion_rate,
            "case_truth": {
                "murderer_name": true_murderer.name,
                "murderer_occupation": true_murderer.occupation,
                "motive": case.murder_motive,
                "modus_operandi": case.murder_method,
                "time_line": case.true_timeline,
            },
            "key_evidence": [
                {"name": c.name, "description": c.description}
                for c in case.clues
                if c.clue_id in [cid for chain in case.evidence_chains for cid in chain.required_clues]
            ],
            "player_performance": {
                "strengths": self._get_player_strengths(is_correct, clue_completion_rate, accuracy_score),
                "weaknesses": self._get_player_weaknesses(is_correct, clue_completion_rate, accuracy_score),
                "improvement_suggestions": self._get_improvement_suggestions(accuracy_score),
            }
        }

    def _generate_case_review(
        self,
        session: GameSession,
        is_correct: bool,
        accuracy_score: int,
        clue_completion_rate: int,
    ) -> Dict[str, Any]:
        """生成探案过程复盘"""
        # 确定侦探等级
        if accuracy_score >= 90:
            rank = "传奇侦探"
            comment = "你的推理能力出神入化，堪称当代福尔摩斯！"
        elif accuracy_score >= 80:
            rank = "名侦探"
            comment = "你的推理非常精彩，是个出色的侦探！"
        elif accuracy_score >= 70:
            rank = "优秀侦探"
            comment = "你的推理能力很强，稍加磨练就能成为名侦探！"
        elif accuracy_score >= 60:
            rank = "合格侦探"
            comment = "你已经具备基本的推理能力，继续努力吧！"
        else:
            rank = "新手侦探"
            comment = "你还需要更多的练习，多积累探案经验哦！"

        return {
            "rank": rank,
            "comment": comment,
            "play_time": int((datetime.now() - session.start_time).total_seconds() / 60),
            "clues_collected": len(session.collected_clues),
            "total_clues": len(session.case.clues),
            "wrong_guess_count": session.wrong_guess_count,
            "dialogue_count": len(session.dialogue_history),
        }

    def _get_player_strengths(self, is_correct: bool, clue_completion_rate: int, accuracy_score: int) -> List[str]:
        """获取玩家优点"""
        strengths = []
        if is_correct:
            strengths.append("成功识别出真正的凶手，逻辑推理能力出色")
        if clue_completion_rate >= 80:
            strengths.append("现场勘查非常仔细，找到了大部分线索")
        if accuracy_score >= 80:
            strengths.append("证据链分析到位，推理逻辑严谨")
        if not strengths:
            strengths.append("参与度很高，积极完成了探案过程")
        return strengths

    def _get_player_weaknesses(self, is_correct: bool, clue_completion_rate: int, accuracy_score: int) -> List[str]:
        """获取玩家不足"""
        weaknesses = []
        if not is_correct:
            weaknesses.append("对真凶的判断出现失误，需要加强逻辑推理能力")
        if clue_completion_rate < 60:
            weaknesses.append("现场勘查不够仔细，遗漏了很多重要线索")
        if accuracy_score < 70:
            weaknesses.append("证据分析能力有待提升，没有抓住关键证据")
        return weaknesses

    def _get_improvement_suggestions(self, accuracy_score: int) -> List[str]:
        """获取改进建议"""
        suggestions = []
        if accuracy_score < 70:
            suggestions.append("建议更加仔细地勘查现场，不要放过任何蛛丝马迹")
            suggestions.append("多注意嫌疑人回答中的矛盾点和异常情绪变化")
        elif accuracy_score < 85:
            suggestions.append("可以更加注重证据之间的关联性，构建完整的推理链条")
            suggestions.append("尝试站在凶手的角度思考作案动机和手法")
        else:
            suggestions.append("你的推理能力已经很优秀了，可以尝试挑战更高难度的案件")
        return suggestions

# 全局实例
judge_agent = JudgeAgent()
