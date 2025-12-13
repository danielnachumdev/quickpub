import logging
import sys
from typing import Optional

# Global log level that can be modified by users
_LOG_LEVEL = logging.INFO


class QuickpubLogFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("quickpub")


class TqdmLoggingHandler(logging.Handler):

    def __init__(self, level: int = logging.NOTSET):
        super().__init__(level)
        self._tqdm = None

    def emit(self, record: logging.LogRecord) -> None:
        try:
            import tqdm

            msg = self.format(record)
            tqdm.tqdm.write(msg, file=sys.stdout)
        except ImportError:
            # Fallback if tqdm becomes unavailable
            print(self.format(record), file=sys.stdout)
        except Exception:
            self.handleError(record)


def setup_logging(level: Optional[int] = None) -> None:
    global _LOG_LEVEL

    if level is not None:
        _LOG_LEVEL = level

    logger = logging.getLogger()
    logger.setLevel(_LOG_LEVEL)

    logger.handlers.clear()

    formatter = logging.Formatter(
        "[quickpub] %(levelname)-5s %(asctime)s %(filename)s:%(lineno)d | %(message)s"
    )

    try:
        import tqdm

        handler: logging.Handler = TqdmLoggingHandler()
    except ImportError:
        handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(_LOG_LEVEL)
    handler.setFormatter(formatter)

    handler.addFilter(QuickpubLogFilter())

    logger.addHandler(handler)


def set_log_level(level: int):
    global _LOG_LEVEL
    _LOG_LEVEL = level

    logger = logging.getLogger()
    logger.setLevel(level)

    for handler in logger.handlers:
        handler.setLevel(level)


__all__ = ["setup_logging", "set_log_level", "QuickpubLogFilter"]
