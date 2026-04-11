#!/usr/bin/env python3
"""测试配置加载问题"""
import os
import sys

print("=" * 60)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path)
print("=" * 60)

# 尝试不同方式导入配置
print("\n--- 测试1: 直接从 app.core.config 导入 ---")
try:
    from app.core.config import settings
    print("✓ 导入成功")
    print(f"OPENAI_API_KEY (前10位): {settings.OPENAI_API_KEY[:10] if settings.OPENAI_API_KEY else '空'}")
    print(f"OPENAI_MODEL: {settings.OPENAI_MODEL}")
    print(f"env_file配置: {settings.model_config.get('env_file')}")
except Exception as e:
    print(f"✗ 导入失败: {e}")

print("\n--- 测试2: 检查 .env 文件是否存在 ---")
env_path = os.path.join(os.getcwd(), ".env")
print(f".env 文件路径: {env_path}")
print(f".env 文件存在: {os.path.exists(env_path)}")
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("\n.env 文件内容 (部分):")
        for line in content.split('\n')[:10]:
            print(f"  {line}")

print("\n--- 测试3: 切换到 backend 目录后再测试 ---")
backend_dir = os.path.dirname(os.path.abspath(__file__))
print(f"backend 目录: {backend_dir}")

os.chdir(backend_dir)
print(f"切换后工作目录: {os.getcwd()}")

# 重新导入（清除模块缓存）
if 'app.core.config' in sys.modules:
    del sys.modules['app.core.config']
if 'app' in sys.modules:
    del sys.modules['app']

try:
    from app.core.config import settings
    print("✓ 导入成功")
    print(f"OPENAI_API_KEY (前10位): {settings.OPENAI_API_KEY[:10] if settings.OPENAI_API_KEY else '空'}")
    print(f"OPENAI_MODEL: {settings.OPENAI_MODEL}")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
