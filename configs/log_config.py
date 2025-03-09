from loguru import logger
import sys

# 移除默认的handler
logger.remove()

# 添加控制台输出
logger.add(sys.stderr, level="INFO",
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | {level} | <cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

# 添加文件输出
logger.add("logs/file_{time}.log",  # 按时间命名的文件
           rotation="500 MB",        # 文件大小超过500MB时轮换
           retention="30 days",      # 保留10天的日志
           level="DEBUG",
           encoding="utf-8",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} - {message}")
