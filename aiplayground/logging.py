from aiplayground.settings import Settings

try:
    from flaskplusplus.logging import logger
except ModuleNotFoundError:
    import logging

    logger = logging.getLogger(__name__)
    logger.setLevel(Settings.LOG_LEVEL)
    sh = logging.StreamHandler(Settings.LOG_LEVEL)
    logger.addHandler(sh)
