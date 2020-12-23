from aiplayground.settings import settings
import logging

logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)
sh = logging.StreamHandler()
sh.setLevel(settings.LOG_LEVEL)
logger.addHandler(sh)
