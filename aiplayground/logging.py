from aiplayground.settings import settings
import logging

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL.upper())
sh = logging.StreamHandler()
sh.setLevel(settings.LOG_LEVEL.upper())
logger.addHandler(sh)
