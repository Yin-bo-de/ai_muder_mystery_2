"""测试修复后的验证问题"""
import pytest
from app.models.case import Clue, Suspect, ContradictionPoint
from app.core.constants import ClueType, ClueStatus, ContradictionType


def test_clue_status_and_importance_validation():
    """测试Clue的status和importance字段验证通过"""
    # 测试合法的status和importance
    clue = Clue(
        clue_id="c_test",
        name="测试线索",
        clue_type=ClueType.PHYSICAL,
        status=ClueStatus.HIDDEN,
        description="测试线索描述",
        location="测试位置",
        scene="test_scene",
        importance=0.9,
        related_suspects=["s1"]
    )
    assert clue.status == ClueStatus.HIDDEN
    assert clue.importance == 0.9

    # 测试importance边界值
    clue2 = Clue(
        clue_id="c_test2",
        name="测试线索2",
        clue_type=ClueType.PHYSICAL,
        status=ClueStatus.DISCOVERED,
        description="测试线索描述2",
        location="测试位置2",
        scene="test_scene2",
        importance=1.0,
        related_suspects=["s1"]
    )
    assert clue2.importance == 1.0

    clue3 = Clue(
        clue_id="c_test3",
        name="测试线索3",
        clue_type=ClueType.PHYSICAL,
        status=ClueStatus.COLLECTED,
        description="测试线索描述3",
        location="测试位置3",
        scene="test_scene3",
        importance=0.0,
        related_suspects=["s1"]
    )
    assert clue3.importance == 0.0


def test_suspect_counter_evidence_is_list():
    """测试Suspect的counter_evidence是List[str]类型"""
    suspect = Suspect(
        suspect_id="s_test",
        name="测试嫌疑人",
        age=30,
        gender="男",
        occupation="职业",
        description="描述",
        personality_traits=["性格1"],
        relationship_with_victim="关系",
        alibi="不在场证明",
        background_story="背景故事",
        counter_evidence=["证据1", "证据2"]
    )
    assert isinstance(suspect.counter_evidence, list)
    assert len(suspect.counter_evidence) == 2
    assert suspect.counter_evidence[0] == "证据1"


def test_contradiction_point_has_contradiction_type():
    """测试ContradictionPoint有contradiction_type字段"""
    cp = ContradictionPoint(
        contradiction_id="cp_test",
        contradiction_type=ContradictionType.TIMELINE,
        description="测试矛盾点",
        involved_suspects=["s1", "s2"],
        trigger_condition={},
        hint_for_user="测试提示"
    )
    assert hasattr(cp, 'contradiction_type')
    assert cp.contradiction_type == ContradictionType.TIMELINE
    assert not hasattr(cp, 'type') or cp.type is None
