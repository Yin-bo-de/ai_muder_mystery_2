"""测试ContradictionPoint模型"""
import pytest
from app.models.case import ContradictionPoint
from app.core.constants import ContradictionType


def test_contradiction_point_has_correct_field():
    """测试ContradictionPoint具有contradiction_type字段而不是type字段"""
    cp = ContradictionPoint(
        contradiction_id="cp_test",
        contradiction_type=ContradictionType.TIMELINE,
        description="测试矛盾点",
        involved_suspects=["s1", "s2"],
        trigger_condition={"requires_both_speaking": True},
        hint_for_user="这是一个测试提示"
    )

    # 验证contradiction_type字段存在且可访问
    assert hasattr(cp, 'contradiction_type')
    assert cp.contradiction_type == ContradictionType.TIMELINE

    # 验证不再有type字段（防止混淆）
    assert not hasattr(cp, 'type') or cp.type is None


def test_create_all_contradiction_types():
    """测试创建所有类型的矛盾点"""
    # 时间线矛盾
    cp_timeline = ContradictionPoint(
        contradiction_id="cp_timeline",
        contradiction_type=ContradictionType.TIMELINE,
        description="时间线矛盾测试",
        involved_suspects=["s1", "s2"],
        trigger_condition={"requires_both_speaking": True},
        hint_for_user="时间线矛盾提示"
    )
    assert cp_timeline.contradiction_type == ContradictionType.TIMELINE

    # 空间矛盾
    cp_spatial = ContradictionPoint(
        contradiction_id="cp_spatial",
        contradiction_type=ContradictionType.SPATIAL,
        description="空间矛盾测试",
        involved_suspects=["s1", "s2"],
        trigger_condition={"requires_both_speaking": True},
        hint_for_user="空间矛盾提示"
    )
    assert cp_spatial.contradiction_type == ContradictionType.SPATIAL

    # 证据矛盾
    cp_evidence = ContradictionPoint(
        contradiction_id="cp_evidence",
        contradiction_type=ContradictionType.EVIDENCE,
        description="证据矛盾测试",
        involved_suspects=["s1"],
        trigger_condition={"requires_both_speaking": False},
        hint_for_user="证据矛盾提示"
    )
    assert cp_evidence.contradiction_type == ContradictionType.EVIDENCE
