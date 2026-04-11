#!/usr/bin/env python3
"""简化版配置测试"""
import os
import sys

print("=" * 60)
print("当前工作目录:", os.getcwd())
print("脚本所在目录:", os.path.dirname(os.path.abspath(__file__)))
print("=" * 60)

# 添加 backend 目录到 Python 路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print(f"\n已添加到 Python 路径: {backend_dir}")

print("\n--- 检查 .env 文件位置 ---")
env_paths = [
    os.path.join(os.getcwd(), ".env"),
    os.path.join(backend_dir, ".env"),
]
for path in env_paths:
    exists = os.path.exists(path)
    print(f"  {path}: {'✓ 存在' if exists else '✗ 不存在'}")

print("\n--- 测试配置加载 ---")
try:
    from app.core.config import settings
    print("✓ settings 导入成功")
    print(f"  OPENAI_MODEL: {settings.OPENAI_MODEL}")
    print(f"  OPENAI_API_KEY: {'已设置' if settings.OPENAI_API_KEY else '未设置'}")
    if settings.OPENAI_API_KEY:
        print(f"  OPENAI_API_KEY (前10位): {settings.OPENAI_API_KEY[:10]}...")

    print(f"\n  Settings model_config:")
    print(f"    env_file: {settings.model_config.get('env_file')}")

except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("结论: Pydantic Settings 默认从当前工作目录查找 .env 文件")
print("如果工作目录不是 backend/, 就找不到 .env 文件")
print("=" * 60)
