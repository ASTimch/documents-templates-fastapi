import logging

from app.config import settings

logger = logging.getLogger()
logger.setLevel(settings.LOG_LEVEL)
