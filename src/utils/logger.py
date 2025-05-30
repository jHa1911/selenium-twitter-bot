import logging
import sys
from pathlib import Path
from loguru import logger
import colorlog

def setup_logger():
    # Remove default loguru handler
    logger.remove()

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # File handler
    logger.add(
        "logs/twitter_bot.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days"
    )

    return logger
