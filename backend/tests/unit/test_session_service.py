"""会话服务单元测试"""
import pytest
from datetime import datetime, timedelta
from app.services.session_service import session_service
from app.models.case import Case, Victim, Suspect, Scene, EvidenceChain, EvidenceChainItem
from app.core.constants import GameStatus


@pytest.fixture
def mock_case():
    """创建模拟案件数据"""
    return Case(
        case_id="test_case_001",
        title="测试案件",
        description="这是一个测试案件",
        difficulty=2,
        theme="modern",
        victim=Victim(
            victim_id="v1",
            name="张三",
            age=45,
            gender="男",
            occupation="公司老板",
            description="中等身材，性格强势，白手起家的企业家",
            cause_of_death="锐器刺伤",
            death_time=datetime(2026, 4, 6, 14, 30, 0),
            death_location="张三的办公室",
            social_relationships={
                "s1": "债主",
                "s2": "同事"
            },
            background_story="白手起家的企业家，近年与多人有利益纠纷，为人强势",
        ),
        suspects=[
            Suspect(
                suspect_id="s1",
                name="李四",
                age=32,
                gender="男",
                occupation="外卖员",
                description="身材壮实，面容憔悴，眼神凶狠",
                personality_traits=["脾气暴躁", "容易冲动", "讲义气"],
                relationship_with_victim="债主",
                motive="死者欠他5万元不还，多次催要无果",
                alibi="案发时我在送外卖，有订单记录",
                alibi_reliability=0.6,
                timeline={
                    "14:00": "在餐馆取餐",
                    "14:20": "送往XX小区",
                    "14:30": "正在送餐路上"
                },
                secrets=["最近赌博输了很多钱，急需用钱", "案发前一天曾去死者公司讨债"],
                is_murderer=True,
                background_story="农村出身，来城市打拼多年，靠送外卖为生，因为母亲生病急需用钱，多次向死者讨债被拒",
            ),
            Suspect(
                suspect_id="s2",
                name="王五",
                age=28,
                gender="男",
                occupation="公司职员",
                description="戴眼镜，身材瘦弱，看起来很斯文",
                personality_traits=["内向", "心思缜密", "自尊心强"],
                relationship_with_victim="同事",
                motive="死者抢了他的晋升名额，还在公开场合羞辱他",
                alibi="案发时我在公司加班，有同事可以作证",
                alibi_reliability=0.8,
                timeline={
                    "13:00": "在公司开会",
                    "14:00": "回工位写代码",
                    "14:30": "还在公司加班"
                },
                secrets=["偷偷挪用了公款，被死者发现", "最近在找新工作"],
                is_murderer=False,
                background_story="名牌大学毕业，进入公司3年，工作能力强但不擅交际，对死者的打压积怨已久",
            ),
        ],
        clues=[],
        scenes=[
            Scene(
                scene_id="scene_office",
                name="办公室",
                description="死者的办公室，整齐但有打斗痕迹",
                items=["desk", "chair", "bookshelf", "safe"]
            )
        ],
        evidence_chains=[
            EvidenceChain(
                chain_id="chain_001",
                name="核心证据链",
                description="证明李四是凶手的证据链",
                items=[
                    EvidenceChainItem(
                        clue_id="clue_001",
                        description="凶器上的指纹属于李四",
                        logical_order=1
                    )
                ],
                conclusion="李四是凶手",
                required_clues=["clue_001"]
            )
        ],
        murderer_id="s1",
        murder_weapon="水果刀",
        murder_motive="母亲生病急需用钱，死者欠5万元不还，多次催要无果，遂起杀意",
        murder_method="以送餐为由进入办公室，趁死者不备拿出事先准备的水果刀刺向死者心脏",
        true_timeline={
            "14:25": "李四到达死者公司楼下",
            "14:28": "李四进入死者办公室",
            "14:30": "李四刺杀死者",
            "14:32": "李四清理现场",
            "14:35": "李四离开公司"
        },
        red_herrings=["王五挪用公款被死者发现"]
    )


class TestSessionService:
    """会话服务测试"""

    def test_create_session(self, mock_case):
        """测试创建会话"""
        session = session_service.create_session("test_user", mock_case)

        assert session.session_id is not None
        assert session.user_id == "test_user"
        assert session.case == mock_case
        assert session.game_status == GameStatus.IN_PROGRESS
        assert len(session.suspect_states) == 2
        assert session.wrong_guess_count == 0

        # 验证会话被存储
        saved_session = session_service.get_session(session.session_id)
        assert saved_session is not None
        assert saved_session.session_id == session.session_id

    def test_get_nonexistent_session(self):
        """测试获取不存在的会话"""
        session = session_service.get_session("non_existent_session")
        assert session is None

    def test_update_session(self, mock_case):
        """测试更新会话"""
        session = session_service.create_session("test_user", mock_case)
        session.wrong_guess_count = 1

        result = session_service.update_session(session)
        assert result is True

        updated_session = session_service.get_session(session.session_id)
        assert updated_session.wrong_guess_count == 1

    def test_update_game_status(self, mock_case):
        """测试更新游戏状态"""
        session = session_service.create_session("test_user", mock_case)

        result = session_service.update_game_status(session.session_id, GameStatus.COMPLETED)
        assert result is True

        updated_session = session_service.get_session(session.session_id)
        assert updated_session.game_status == GameStatus.COMPLETED

    def test_increment_wrong_guess(self, mock_case):
        """测试增加错误指认次数"""
        session = session_service.create_session("test_user", mock_case)

        # 第一次错误
        count = session_service.increment_wrong_guess(session.session_id)
        assert count == 1
        assert session_service.get_session(session.session_id).wrong_guess_count == 1
        assert session_service.get_session(session.session_id).game_status == GameStatus.IN_PROGRESS

        # 第二次错误
        count = session_service.increment_wrong_guess(session.session_id)
        assert count == 2
        assert session_service.get_session(session.session_id).wrong_guess_count == 2
        assert session_service.get_session(session.session_id).game_status == GameStatus.FAILED

    def test_delete_session(self, mock_case):
        """测试删除会话"""
        session = session_service.create_session("test_user", mock_case)
        session_id = session.session_id

        result = session_service.delete_session(session_id)
        assert result is True

        deleted_session = session_service.get_session(session_id)
        assert deleted_session is None

    def test_cleanup_expired_sessions(self, mock_case):
        """测试清理过期会话"""
        # 创建一个正常会话
        session1 = session_service.create_session("test_user", mock_case)

        # 创建一个过期会话（手动修改最后活跃时间）
        session2 = session_service.create_session("test_user", mock_case)
        session2.last_active_time = datetime.now() - timedelta(hours=25)
        # 直接修改sessions字典，避免update_session更新last_active_time
        from app.services.session_service import sessions
        sessions[session2.session_id] = session2

        # 清理过期会话
        cleaned_count = session_service.cleanup_expired_sessions()
        assert cleaned_count == 1

        # 验证会话1存在，会话2被删除
        assert session_service.get_session(session1.session_id) is not None
        assert session_service.get_session(session2.session_id) is None

    def test_add_user_operation(self, mock_case):
        """测试添加用户操作记录"""
        session = session_service.create_session("test_user", mock_case)

        result = session_service.add_user_operation(
            session.session_id,
            "investigate",
            {"scene": "客厅", "item": "桌子"}
        )
        assert result is True

        updated_session = session_service.get_session(session.session_id)
        assert len(updated_session.user_operations) == 1
        assert updated_session.user_operations[0].operation_type == "investigate"
        assert updated_session.user_operations[0].details["scene"] == "客厅"
