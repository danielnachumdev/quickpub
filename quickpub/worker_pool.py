import logging
from danielutils import AsyncWorkerPool

logger = logging.getLogger(__name__)


class WorkerPool(AsyncWorkerPool):
    @staticmethod
    def log(level: int, message: str, *args, **kwargs):
        logger.log(level, message, *args, **kwargs)


__all__ = [
    'WorkerPool',
]
