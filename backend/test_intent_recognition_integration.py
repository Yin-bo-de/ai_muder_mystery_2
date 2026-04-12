#!/usr/bin/env python3
"""简单的集成验证脚本：测试意图识别Agent的集成"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from app.models.case import Suspect
from app.models.agent import Message
from app.agents.dialogue_manager import DialogueManager
from app.agents.intent_recognition_agent import (
    IntentRecognitionAgent,
    IntentRecognitionResult,
    UserIntent,
)
from app.utils.logger import logger


def test_intent_recognition_agent_init():
    """测试意图识别Agent初始化"""
    print("=" * 60)
    print("测试 1: 意图识别Agent初始化")
    print("=" * 60)

    suspect_data = {
        "suspect_001": "张三",
        "suspect_002": "李四",
        "suspect_003": "王五",
    }

    try:
        agent = IntentRecognitionAgent(suspect_data)
        print(f"✅ Agent初始化成功")
        print(f"   - suspect_id_to_name: {agent.suspect_id_to_name}")
        print(f"   - suspect_name_to_id: {agent.suspect_name_to_id}")
        return True, agent
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_prompt_building(agent):
    """测试提示词构建"""
    print("\n" + "=" * 60)
    print("测试 2: 提示词构建")
    print("=" * 60)

    try:
        prompt = agent._build_prompt()
        print(f"✅ 提示词构建成功")
        print(f"   - 提示词类型: {type(prompt)}")
        print(f"   - 消息数量: {len(prompt.messages)}")

        # 检查提示词内容
        template_text = prompt.messages[0].prompt.template
        sections = [
            "嫌疑人列表",
            "对话历史",
            "当前问题",
            "任务",
            "详细注意事项和示例场景",
            "输出格式要求",
        ]

        missing = [s for s in sections if s not in template_text]
        if missing:
            print(f"⚠️  警告: 提示词缺少部分: {missing}")
        else:
            print(f"✅ 提示词包含所有必要部分")

        return True
    except Exception as e:
        print(f"❌ 提示词构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dialogue_manager_integration():
    """测试DialogueManager集成"""
    print("\n" + "=" * 60)
    print("测试 3: DialogueManager集成")
    print("=" * 60)

    try:
        # 创建测试嫌疑人
        suspects = [
            Suspect(
                suspect_id="suspect_001",
                name="张三",
                age=35,
                gender="男",
                occupation="医生",
                relationship_with_victim="同事",
                motive="",
                alibi="昨晚在医院值班",
                secrets="",
                personality_traits=["冷静", "理性"],
                is_murderer=False,
            ),
            Suspect(
                suspect_id="suspect_002",
                name="李四",
                age=28,
                gender="女",
                occupation="护士",
                relationship_with_victim="下属",
                motive="",
                alibi="昨晚在家休息",
                secrets="",
                personality_traits=["温柔", "内向"],
                is_murderer=False,
            ),
        ]

        # 创建DialogueManager
        manager = DialogueManager(suspects, "suspect_001")
        print(f"✅ DialogueManager创建成功")

        # 检查intent_recognition_agent是否初始化
        if manager.intent_recognition_agent:
            print(f"✅ 意图识别Agent已初始化")
        else:
            print(f"⚠️  意图识别Agent未启用（检查配置ENABLE_INTENT_RECOGNITION_AGENT）")

        # 检查是否有新方法
        has_async_method = hasattr(manager, "_analyze_user_intent_with_context")
        has_validate_method = hasattr(manager, "_validate_result")

        print(f"   - _analyze_user_intent_with_context: {'✅' if has_async_method else '❌'}")
        print(f"   - _validate_result: {'✅' if has_validate_method else '❌'}")

        # 检查_determine_reply_priority是否是异步的
        import inspect
        method = getattr(manager, "_determine_reply_priority")
        is_async = inspect.iscoroutinefunction(method)
        print(f"   - _determine_reply_priority is async: {'✅' if is_async else '❌'}")

        return has_async_method and has_validate_method and is_async

    except Exception as e:
        print(f"❌ DialogueManager集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rule_based_intent():
    """测试基于规则的意图识别（兜底机制）"""
    print("\n" + "=" * 60)
    print("测试 4: 基于规则的意图识别（兜底）")
    print("=" * 60)

    try:
        # 创建测试嫌疑人和Manager
        suspects = [
            Suspect(
                suspect_id="suspect_001",
                name="张三",
                age=35,
                gender="男",
                occupation="医生",
                relationship_with_victim="同事",
                motive="",
                alibi="昨晚在医院值班",
                secrets="",
                personality_traits=["冷静", "理性"],
                is_murderer=False,
            ),
        ]

        manager = DialogueManager(suspects, "suspect_001")

        # 禁用意图识别Agent，只测试规则
        manager.intent_recognition_agent = None

        # 测试各种场景
        test_cases = [
            ("大家好", UserIntent.ALL, ["suspect_001"]),
            ("张三，你在哪？", UserIntent.SINGLE, ["suspect_001"]),
            ("所有人都说说", UserIntent.ALL, ["suspect_001"]),
            ("什么情况？", UserIntent.ALL, ["suspect_001"]),
        ]

        all_passed = True
        for message, expected_intent, expected_targets in test_cases:
            intent, targets = manager._analyze_user_intent(message)
            passed = intent == expected_intent and set(targets) == set(expected_targets)
            status = "✅" if passed else "❌"
            print(f"{status} '{message}' → intent={intent}, targets={targets}")
            if not passed:
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ 规则意图识别测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("意图识别Agent集成验证")
    print("=" * 60)

    results = []

    # 测试1: Agent初始化
    success, agent = test_intent_recognition_agent_init()
    results.append(("Agent初始化", success))

    # 测试2: 提示词构建
    if agent:
        success = test_prompt_building(agent)
        results.append(("提示词构建", success))

    # 测试3: DialogueManager集成
    success = test_dialogue_manager_integration()
    results.append(("DialogueManager集成", success))

    # 测试4: 规则意图识别
    success = test_rule_based_intent()
    results.append(("规则意图识别", success))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")

    all_passed = all(success for _, success in results)

    if all_passed:
        print("\n🎉 所有集成测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查！")
        return 1


if __name__ == "__main__":
    exit(main())
