"""线索服务单元测试"""
import pytest
from app.services.clue_service import clue_service
from app.services.session_service import session_service
from app.models.case import Case, Victim, Suspect, Clue, Scene, EvidenceChain, EvidenceChainItem
from app.core.constants import ClueType, ClueStatus


@pytest.fixture
def mock_case():
    """创建模拟案件数据"""
    from datetime import datetime
    return Case(
        case_id="test_case_001",
        title="测试案件",
        description="这是一个测试案件",
        difficulty=2,
        victim=Victim(
            victim_id="v1",
            name="张三",
            age=45,
            gender="男",
            occupation="公司老板",
            description="中等身材，性格强势",
            cause_of_death="锐器刺伤",
            death_time=datetime(2026, 4, 6, 14, 30, 0),
            death_location="张三家中客厅",
            background_story="白手起家的企业家，近年与多人有利益纠纷",
        ),
        suspects=[
            Suspect(
                suspect_id="s1",
                name="李四",
                age=32,
                gender="男",
                occupation="外卖员",
                description="身材偏瘦，性格急躁",
                personality_traits=["脾气暴躁", "容易冲动"],
                relationship_with_victim="债主",
                motive="死者欠他5万元不还",
                alibi="案发时我在送外卖",
                alibi_reliability=0.3,
                background_story="外卖员，最近赌博输了很多钱，急需用钱",
                is_murderer=True,
            ),
        ],
        clues=[
            Clue(
                clue_id="c1",
                name="带血的水果刀",
                description="一把水果刀，上面有血迹",
                clue_type=ClueType.PHYSICAL,
                status=ClueStatus.HIDDEN,
                scene="客厅",
                location="客厅茶几下面",
                points_to_suspect="s1",
                related_clues=["c2"],
                related_suspects=["s1"],
            ),
            Clue(
                clue_id="c2",
                name="外卖订单",
                description="一张外卖订单，时间是案发当天14:20",
                clue_type=ClueType.PHYSICAL,
                status=ClueStatus.HIDDEN,
                scene="门口",
                location="门口鞋柜上",
                points_to_suspect="s1",
                related_suspects=["s1"],
            ),
            Clue(
                clue_id="c3",
                name="邻居证词",
                description="邻居说案发时看到一个穿外卖服的人匆匆离开",
                clue_type=ClueType.TESTIMONY,
                status=ClueStatus.HIDDEN,
                scene="客厅",
                location="客厅窗户边",
                points_to_suspect="s1",
            ),
        ],
        scenes=[
            Scene(
                scene_id="scene_living_room",
                name="客厅",
                description="死者家中客厅，有打斗痕迹",
                items=["茶几", "沙发", "电视柜", "窗户", "鞋柜"],
                is_crime_scene=True,
            )
        ],
        evidence_chains=[
            EvidenceChain(
                chain_id="chain_001",
                name="核心证据链",
                description="证明李四是凶手的证据链",
                items=[
                    EvidenceChainItem(
                        clue_id="c1",
                        description="凶器上有李四的指纹",
                        logical_order=1,
                    )
                ],
                conclusion="李四是凶手",
                required_clues=["c1", "c2", "c3"],
            )
        ],
        murderer_id="s1",
        murder_weapon="水果刀",
        murder_motive="死者欠他5万元不还，催债多次未果",
        murder_method="趁死者开门取外卖时，用随身携带的水果刀刺死死者",
    )


@pytest.fixture
def test_session(mock_case):
    """创建测试会话"""
    session = session_service.create_session("test_user", mock_case)
    # 添加一些已收集的线索
    session.collected_clues = [
        Clue(
            clue_id="c1",
            name="带血的水果刀",
            description="一把水果刀，上面有血迹",
            clue_type=ClueType.PHYSICAL,
            status=ClueStatus.COLLECTED,
            scene="客厅",
            location="客厅茶几下面",
            points_to_suspect="s1",
            related_suspects=["s1"],
        ),
        Clue(
            clue_id="c2",
            name="外卖订单",
            description="一张外卖订单，时间是案发当天14:20",
            clue_type=ClueType.PHYSICAL,
            status=ClueStatus.COLLECTED,
            scene="门口",
            location="门口鞋柜上",
            points_to_suspect="s1",
            related_suspects=["s1"],
        ),
    ]
    session_service.update_session(session)
    return session


class TestClueService:
    """线索服务测试"""

    def test_get_collected_clues(self, test_session):
        """测试获取已收集线索"""
        clues = clue_service.get_collected_clues(test_session.session_id)
        assert len(clues) == 2
        assert {c.clue_id for c in clues} == {"c1", "c2"}

    def test_get_collected_clues_by_type(self, test_session):
        """测试按类型获取线索"""
        physical_clues = clue_service.get_collected_clues(test_session.session_id, ClueType.PHYSICAL)
        assert len(physical_clues) == 2

        testimony_clues = clue_service.get_collected_clues(test_session.session_id, ClueType.TESTIMONY)
        assert len(testimony_clues) == 0

    def test_get_clue_detail(self, test_session):
        """测试获取线索详情"""
        clue = clue_service.get_clue_detail(test_session.session_id, "c1")
        assert clue is not None
        assert clue.clue_id == "c1"
        assert clue.name == "带血的水果刀"
        assert clue.clue_type == ClueType.PHYSICAL

    def test_get_clue_statistics(self, test_session):
        """测试获取线索统计信息"""
        stats = clue_service.get_clue_statistics(test_session.session_id)
        assert stats["total_clues"] == 3
        assert stats["collected_clues"] == 2
        assert stats["completion_rate"] == 67
        assert stats["type_statistics"][ClueType.PHYSICAL] == 2
        assert stats["scene_statistics"]["客厅"] == 1
        assert stats["scene_statistics"]["门口"] == 1

    def test_get_related_clues(self, test_session):
        """测试获取相关线索"""
        related_clues = clue_service.get_related_clues(test_session.session_id, "c1")
        assert len(related_clues) == 1
        assert related_clues[0].clue_id == "c2"

    def test_associate_clues(self, test_session):
        """测试关联线索"""
        result = clue_service.associate_clues(test_session.session_id, ["c1", "c2"])
        assert result["success"] is True
        assert "共同指向嫌疑人" in result["message"]
        assert len(result["common_suspects"]) == 1
        assert result["common_suspects"][0] == "s1"

        # 验证线索状态更新为已关联
        updated_session = session_service.get_session(test_session.session_id)
        for clue in updated_session.collected_clues:
            assert clue.status == ClueStatus.ASSOCIATED

    def test_associate_clues_less_than_two(self, test_session):
        """测试关联少于2条线索"""
        result = clue_service.associate_clues(test_session.session_id, ["c1"])
        assert result["success"] is False
        assert "至少需要选择两个线索" in result["message"]

    def test_get_undiscovered_clue_hints(self, test_session):
        """测试获取未发现线索提示"""
        hints = clue_service.get_undiscovered_clue_hints(test_session.session_id)
        assert len(hints) >= 1
        assert "客厅" in hints[0]["hint"]  # 未发现的线索在客厅
