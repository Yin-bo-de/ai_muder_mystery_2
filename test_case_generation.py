#!/usr/bin/env python3
"""测试案件生成功能"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.agents.case_generator_agent import case_generator
from app.utils.logger import logger


async def test_case_generation():
    """测试案件生成"""
    try:
        logger.info("开始测试案件生成功能...")
        case = await case_generator.generate_case(difficulty="medium")

        logger.info(f"✅ 案件生成成功！")
        logger.info(f"案件ID: {case.case_id}")
        logger.info(f"案件标题: {case.title}")
        logger.info(f"死者: {case.victim.name}，{case.victim.age}岁，{case.victim.occupation}")
        logger.info(f"死亡原因: {case.victim.death_cause}，死亡时间: {case.victim.death_time}")
        logger.info(f"嫌疑人数量: {len(case.suspects)}")

        for i, suspect in enumerate(case.suspects):
            logger.info(f"\n嫌疑人{i+1}: {suspect.name}")
            logger.info(f"  年龄: {suspect.age}, 职业: {suspect.occupation}")
            logger.info(f"  与死者关系: {suspect.relationship_with_victim}")
            logger.info(f"  动机: {suspect.motive}")
            logger.info(f"  不在场证明: {suspect.alibi}")

        logger.info(f"\n真凶ID: {case.true_murderer_id}")
        logger.info(f"作案手法: {case.modus_operandi}")
        logger.info(f"线索数量: {len(case.clues)}")
        logger.info(f"证据链关键证据数量: {len(case.evidence_chain.key_evidence_ids) if case.evidence_chain else 0}")

        logger.info("\n🎉 案件生成功能测试完全正常！")
        logger.info("\n📋 现在可以启动完整服务进行游戏体验：")
        logger.info("1. 启动后端: cd backend && uvicorn main:app --reload --port 8000")
        logger.info("2. 启动前端: cd frontend && npm run dev")
        logger.info("3. 访问 http://localhost:5173 开始游戏")

        return True

    except Exception as e:
        logger.error(f"❌ 案件生成失败: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_case_generation())
    sys.exit(0 if success else 1)
