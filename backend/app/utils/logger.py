import sys
from pathlib import Path
from loguru import logger

# 日志文件路径
LOG_PATH = Path("logs")
LOG_PATH.mkdir(exist_ok=True)

# 日志格式
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# 移除默认处理器
logger.remove()

# 添加控制台处理器
logger.add(
    sys.stdout,
    format=LOG_FORMAT,
    level="DEBUG",
    enqueue=True,
)

# 添加文件处理器
logger.add(
    LOG_PATH / "app_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="INFO",
    rotation="00:00",  # 每天零点轮转
    retention="30 days",  # 保留30天日志
    compression="zip",  # 压缩旧日志
    enqueue=True,
    encoding="utf-8",
)

# 错误日志单独存储
logger.add(
    LOG_PATH / "error_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level="ERROR",
    rotation="00:00",
    retention="30 days",
    compression="zip",
    enqueue=True,
    encoding="utf-8",
)

# 导出logger实例
__all__ = ["logger"]
