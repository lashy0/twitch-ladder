import logging
import sys
from types import FrameType
from typing import cast

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2

        while frame and frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_logging() -> None:
    logger.remove()

    is_json = settings.LOG_FORMAT == "json"

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        serialize=is_json,
        backtrace=settings.LOG_BACKTRACE,
        diagnose=settings.LOG_DIAGNOSE,
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    for logger_name in (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "sqlalchemy",
    ):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
