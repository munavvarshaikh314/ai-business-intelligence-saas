import logging
import sys
from datetime import datetime

def get_logger(name: str = "ai_bi_dashboard") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

class LoggingService:
    _logger = get_logger()

    @classmethod
    def info(cls, msg: str, **kwargs):
        cls._logger.info(msg, extra=kwargs)

    @classmethod
    def warning(cls, msg: str, **kwargs):
        cls._logger.warning(msg, extra=kwargs)

    @classmethod
    def error(cls, msg: str, **kwargs):
        cls._logger.error(msg, extra=kwargs)

    @classmethod
    def debug(cls, msg: str, **kwargs):
        cls._logger.debug(msg, extra=kwargs)

    @classmethod
    def log_request(cls, user_id: str, action: str, dataset_id: str = None, tokens: int = 0):
        cls._logger.info(
            f"REQUEST | user={user_id} | action={action} | dataset={dataset_id} | tokens={tokens}"
        )
