"""游戏服务：核心游戏流程管理"""
from typing import Dict, Any, List, Optional
import random
from datetime import datetime

from app.core.config import settings
from app.core.constants import GameStatus, OperationType, ClueStatus
from app.core.exceptions import (
    SessionNotFoundException,
    GameCompletedException,
    ClueNotFoundException,
    ClueDecryptException,
    AccusationInvalidException,
)
from app.models.case import Case, Clue
from app.models.game import GameStatusResponse
from app.agents.case_generator_agent import case_generator
from app.agents.dialogue_manager import DialogueManager
from app.agents.judge_agent import judge_agent
from .session_service import session_service
from app.utils.logger import logger

# 对话管理器实例缓存（每个会话对应一个）
dialogue_managers: Dict[str, DialogueManager] = {}

class GameService:
    """游戏核心服务"""

    @staticmethod
    async def create_new_game(user_id: str = "default_user", difficulty: str = "medium") -> Dict[str, Any]:
        """
        创建新游戏
        :param user_id: 用户ID
        :param difficulty: 案件难度
        :return: 会话ID和案件基础信息
        """
        # 生成案件
        case = await case_generator.generate_case(difficulty)

        # 创建会话
        session = session_service.create_session(user_id, case)

        # 初始化对话管理器
        dialogue_manager = DialogueManager(case.suspects, case.murderer_id)
        dialogue_managers[session.session_id] = dialogue_manager

        # 记录操作
        session_service.add_user_operation(
            session.session_id,
            OperationType.INVESTIGATE,
            {"case_id": case.case_id, "difficulty": difficulty}
        )

        logger.info(f"新游戏创建成功，会话ID: {session.session_id}，案件ID: {case.case_id}")

        return {
            "session_id": session.session_id,
            "case_basic_info": {
                "case_id": case.case_id,
                "title": case.title,
                "description": case.description,
                "difficulty": difficulty,
                "victim_name": case.victim.name,
                "death_time": case.victim.death_time,
                "death_cause": case.victim.cause_of_death,
                "scene": case.scenes[0].name if case.scenes else "未知",
            },
            "suspects": [
                {
                    "suspect_id": s.suspect_id,
                    "name": s.name,
                    "age": s.age,
                    "gender": s.gender,
                    "occupation": s.occupation,
                    "relationship_with_victim": s.relationship_with_victim,
                    "avatar": s.avatar,
                }
                for s in case.suspects
            ],
            "scenes": [
                {
                    "scene_id": s.scene_id,
                    "name": s.name,
                    "description": s.description,
                    "is_locked": s.is_locked,
                }
                for s in case.scenes
            ],
        }

    @staticmethod
    def get_game_status(session_id: str) -> GameStatusResponse:
        """
        获取游戏状态
        :param session_id: 会话ID
        :return: 游戏状态信息
        """
        from app.models.case import CaseBasicInfo
        from app.core.constants import SuspectMood

        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        # 获取嫌疑人状态
        dialogue_manager = dialogue_managers.get(session_id)
        suspect_states_dict: Dict[str, SuspectState] = {}

        # 优先使用 session 中的 suspect_states
        if session.suspect_states:
            suspect_states_dict = session.suspect_states
        elif dialogue_manager:
            states_list = dialogue_manager.get_suspect_state()
            # 将字典列表转换为 SuspectState 对象字典
            for state_dict in states_list:
                if isinstance(state_dict, dict) and 'suspect_id' in state_dict:
                    suspect_id = state_dict['suspect_id']
                    # 转换为 SuspectState 对象
                    suspect_state = SuspectState(
                        suspect_id=suspect_id,
                        mood=SuspectMood(state_dict.get('mood', 'calm')),
                        pressure_level=float(state_dict.get('stress_level', 0.0)),
                        lies_count=int(state_dict.get('lied_count', 0))
                    )
                    suspect_states_dict[suspect_id] = suspect_state

        # 构建案件基础信息
        case_basic = CaseBasicInfo(
            case_id=session.case.case_id,
            title=session.case.title,
            description=session.case.description,
            victim_name=session.case.victim.name,
            suspect_count=len(session.case.suspects),
            scenes=session.case.scenes,
            difficulty=session.case.difficulty
        )

        return GameStatusResponse(
            session_id=session.session_id,
            game_status=session.game_status,
            case_basic=case_basic,
            suspect_states=suspect_states_dict,
            collected_clue_count=len(session.collected_clues),
            total_clue_count=len(session.case.clues),
            clue_reveal_count=session.clue_reveal_count,
            wrong_guess_count=session.wrong_guess_count,
            current_mode=session.current_mode,
            target_suspect=session.target_suspect,
            reasoning_score=session.reasoning_score,
            elapsed_time=int((datetime.now() - session.start_time).total_seconds()),
        )

    @staticmethod
    def submit_investigation(
        session_id: str,
        scene: str,
        item: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        提交勘查操作
        :param session_id: 会话ID
        :param scene: 勘查场景
        :param item: 勘查物品（可选）
        :return: 勘查结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if session.game_status != GameStatus.IN_PROGRESS:
            raise GameCompletedException()

        # 获取已收集的线索ID列表
        collected_clue_ids = [c.clue_id for c in session.collected_clues]

        # 查找该场景的线索 - 只返回未发现且未收集的线索
        case = session.case
        scene_clues = [
            clue for clue in case.clues
            if clue.scene == scene
            and clue.status == ClueStatus.UNDISCOVERED
            and clue.clue_id not in collected_clue_ids
        ]

        found_clue = None
        already_collected = False

        if scene_clues and random.random() < 0.7:  # 70%概率找到线索
            # 随机选一个线索
            found_clue = random.choice(scene_clues)

            # 双重检查：确保这个线索确实没有被收集过
            if found_clue.clue_id in collected_clue_ids:
                logger.warning(f"线索 {found_clue.clue_id} 已被收集，跳过重复添加")
                found_clue = None
                already_collected = True
            else:
                found_clue.status = ClueStatus.DISCOVERED
                session.collected_clues.append(found_clue)

                # 更新会话
                session_service.update_session(session)

                logger.info(f"会话 {session_id} 在场景 {scene} 找到线索: {found_clue.name}")

        # 记录操作
        session_service.add_user_operation(
            session_id,
            OperationType.INVESTIGATE,
            {"scene": scene, "item": item, "found_clue": found_clue.clue_id if found_clue else None}
        )

        if already_collected:
            message = f"在{scene}勘查完成，但线索已被收集过了"
        else:
            message = f"在{scene}勘查完成" + (f"，发现了线索：{found_clue.name}" if found_clue else "，没有发现有价值的线索")

        return {
            "success": True,
            "clue_found": found_clue is not None,
            "clue": found_clue.dict() if found_clue else None,
            "message": message,
        }

    @staticmethod
    def decrypt_clue(
        session_id: str,
        clue_id: str,
        password: Optional[str] = None,
        related_clues: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        提交线索解密
        :param session_id: 会话ID
        :param clue_id: 线索ID
        :param password: 解密密码（可选）
        :param related_clues: 关联线索ID列表（可选）
        :return: 解密结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if session.game_status != GameStatus.IN_PROGRESS:
            raise GameCompletedException()

        # 查找线索
        clue = next((c for c in session.collected_clues if c.clue_id == clue_id), None)
        if not clue:
            raise ClueNotFoundException()

        if clue.status == ClueStatus.DECRYPTED:
            return {
                "success": True,
                "already_decrypted": True,
                "decrypted_content": clue.description,
                "message": "该线索已经解密过了",
            }

        # 验证解密条件
        # 简单解密验证逻辑，v1.0简化实现
        unlock_success = False

        # 验证密码
        if clue.required_password:
            if password and password == clue.required_password:
                unlock_success = True

        # 验证关联线索
        if clue.required_clues and len(clue.required_clues) > 0:
            if related_clues and set(clue.required_clues).issubset(set(c.clue_id for c in session.collected_clues)):
                unlock_success = True

        # 如果有解密条件但都不满足，抛出异常
        if (clue.required_password or (clue.required_clues and len(clue.required_clues) > 0)) and not unlock_success:
            raise ClueDecryptException()

        # 更新线索状态
        clue.status = ClueStatus.DECRYPTED
        session_service.update_session(session)

        # 记录操作
        session_service.add_user_operation(
            session_id,
            OperationType.DECRYPT,
            {"clue_id": clue_id, "success": True}
        )

        logger.info(f"会话 {session_id} 解密线索成功: {clue_id}")

        return {
            "success": True,
            "decrypted_content": clue.description,
            "message": "解密成功！",
        }

    @staticmethod
    async def submit_accusation(
        session_id: str,
        suspect_id: str,
        motive: str,
        modus_operandi: str,
        evidence: List[str],
    ) -> Dict[str, Any]:
        """
        提交指认
        :param session_id: 会话ID
        :param suspect_id: 指认的嫌疑人ID
        :param motive: 玩家陈述的动机
        :param modus_operandi: 玩家陈述的作案手法
        :param evidence: 玩家提供的证据ID列表
        :return: 指认结果
        """
        session = session_service.get_session(session_id)
        if not session:
            raise SessionNotFoundException()

        if session.game_status == GameStatus.COMPLETED:
            raise GameCompletedException("案件已结案，无法重复指认")

        if session.game_status == GameStatus.FAILED:
            raise GameCompletedException("游戏已失败，请重新开始")

        # 校验参数
        if not suspect_id or not motive or not modus_operandi or evidence is None:
            raise AccusationInvalidException("指认信息不完整，请补充必要信息")

        # 调用裁判Agent判断
        judge_result = await judge_agent.judge_accusation(
            session=session,
            accused_suspect_id=suspect_id,
            player_motive=motive,
            player_modus_operandi=modus_operandi,
            player_evidence=evidence,
        )

        # 更新游戏状态
        if judge_result["is_correct"]:
            session.game_status = GameStatus.COMPLETED
            logger.info(f"会话 {session_id} 指认正确，案件告破")
        else:
            wrong_count = session_service.increment_wrong_guess(session_id)
            logger.info(f"会话 {session_id} 指认错误，当前错误次数: {wrong_count}")

        # 更新会话
        session_service.update_session(session)

        # 记录操作
        session_service.add_user_operation(
            session_id,
            OperationType.ACCUSE,
            {
                "suspect_id": suspect_id,
                "is_correct": judge_result["is_correct"],
                "accuracy_score": judge_result["accuracy_score"],
            }
        )

        return judge_result

    @staticmethod
    def get_dialogue_manager(session_id: str) -> Optional[DialogueManager]:
        """获取会话对应的对话管理器"""
        session = session_service.get_session(session_id)
        if not session:
            return None

        if session_id not in dialogue_managers:
            # 如果不存在，重新创建
            dialogue_managers[session_id] = DialogueManager(
                session.case.suspects,
                session.case.murderer_id
            )

        return dialogue_managers[session_id]

# 全局实例
game_service = GameService()
