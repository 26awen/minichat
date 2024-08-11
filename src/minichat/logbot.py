from loguru import logger
import sys

logger.add("./logs/threads.log", rotation="500MB")
