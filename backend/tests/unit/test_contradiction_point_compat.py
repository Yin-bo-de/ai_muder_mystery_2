"""测试ContradictionPoint兼容性"""
import pytest
from app.models.case import ContradictionPoint
from app.core.constants import ContradictionType


def test_contradiction_point_with_llm_format():
    """测试LLM输出格式的解析（带trigger_keywords等字段）"""
    cp = ContradictionPoint(
        contradiction_id="cp1",
        contradiction_type=ContradictionType.TIMELINE,
        description="时间线矛盾测试",
        involved_suspects=["s1", "s2"],
        trigger_keywords=["时间", "看到"],
        requires_both_speaking=True,
        refuting_suspect="s1",
        refutation_target="s2"
    )

    # 验证自动转换到trigger_condition
    assert cp.trigger_condition is not None
    assert cp.trigger_condition.get("keywords") == ["时间", "看到"]
    assert cp.trigger_condition.get("requires_both_speaking") is True

    # 验证hint_for_user自动生成
    assert cp.hint_for_user is not None
    assert "时间线矛盾测试" in cp.hint_for_user

    # 验证兼容字段存在
    assert cp.refuting_suspect == "s1"
    assert cp.refutation_target == "s2"


def test_contradiction_point_with_native_format():
    """测试原生格式的解析（带trigger_condition和hint_for_user）"""
    cp = ContradictionPoint(
        contradiction_id="cp2",
        contradiction_type=ContradictionType.SPATIAL,
        description="空间矛盾测试",
        involved_suspects=["s1", "s2"],
        trigger_condition={
            "keywords": ["车库", "看到"],
            "requires_both_speaking": True
        },
        hint_for_user="这是原生提示"
    )

    # 验证原生字段保留
    assert cp.trigger_condition.get("keywords") == ["车库", "看到"]
    assert cp.hint_for_user == "这是原生提示"


def test_contradiction_point_mixed_format():
    """测试混合格式（两者都有，原生优先）"""
    cp = ContradictionPoint(
        contradiction_id="cp3",
        contradiction_type=ContradictionType.EVIDENCE,
        description="证据矛盾测试",
        involved_suspects=["s1"],
        trigger_keywords=["刀具", "血迹"],  # LLM格式
        requires_both_speaking=False,  # LLM格式
        trigger_condition={  # 原生格式优先
            "keywords": ["原生关键词"],
            "requires_both_speaking": True
        },
        hint_for_user="原生提示"
    )

    # 原生格式优先
    assert cp.trigger_condition.get("keywords") == ["原生关键词"]
    assert cp.trigger_condition.get("requires_both_speaking") is True
    assert cp.hint_for_user == "原生提示"
