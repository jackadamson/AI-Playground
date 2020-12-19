from aiplayground.settings import settings

try:
    from flaskplusplus.logging import logger
except ModuleNotFoundError:
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(settings.LOG_LEVEL)
    sh = logging.StreamHandler(settings.LOG_LEVEL)
    logger.addHandler(sh)
