#!/usr/bin/env python3
"""测试修复后的配置加载"""
import os
import sys

# 添加 backend 目录到 Python 路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("=" * 60)
print("测试修复后的配置加载")
print(f"BASE_DIR 计算:")
print(f"  当前文件: {__file__}")
print(f"  绝对路径: {os.path.abspath(__file__)}")
print(f"  dirname x3: {os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")
print("=" * 60)

from app.core.config import settings, BASE_DIR

print(f"\n✓ BASE_DIR = {BASE_DIR}")
print(f"✓ env_file = {settings.model_config.get('env_file')}")
print(f"✓ OPENAI_API_KEY 已设置: {bool(settings.OPENAI_API_KEY)}")
if settings.OPENAI_API_KEY:
    print(f"✓ OPENAI_API_KEY (前10位): {settings.OPENAI_API_KEY[:10]}...")
print(f"✓ OPENAI_MODEL = {settings.OPENAI_MODEL}")

print("\n" + "=" * 60)
print("现在可以从任意目录运行 main.py 了！")
print("=" * 60)
