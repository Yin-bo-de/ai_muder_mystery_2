"""Pytest配置文件 - 解决模块导入问题"""
import sys
from pathlib import Path

# 将项目根目录添加到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
