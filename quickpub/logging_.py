import logging
import sys

# Global log level that can be modified by users
_LOG_LEVEL = logging.INFO

class QuickpubLogFilter(logging.Filter):
    """
    Filter that only allows logs from the quickpub package.
    """
    
    def filter(self, record):
        return record.name.startswith('quickpub')

class TqdmLoggingHandler(logging.Handler):
    """
    Custom logging handler that uses tqdm.write to avoid conflicts with progress bars.
    """

    def __init__(self, level: int = logging.NOTSET):
        super().__init__(level)
        self._tqdm = None

    def emit(self, record):
        try:
            import tqdm
            msg = self.format(record)
            tqdm.tqdm.write(msg, file=sys.stdout)
        except ImportError:
            # Fallback if tqdm becomes unavailable
            print(self.format(record), file=sys.stdout)
        except Exception:
            self.handleError(record)

def setup_logging(level: int = None):
    """
    Set up logging with appropriate handler based on tqdm availability.

    If tqdm is installed, uses tqdm.write for output to avoid conflicts with progress bars.
    If tqdm is not installed, uses a standard StreamHandler to stdout.

    Args:
        level: Logging level (default: uses the global _LOG_LEVEL constant)

    Returns:
        Configured logger instance
    """
    global _LOG_LEVEL
    
    # Use provided level or fall back to global constant
    if level is not None:
        _LOG_LEVEL = level
    
    logger = logging.getLogger()
    logger.setLevel(_LOG_LEVEL)

    # Clear any existing handlers
    logger.handlers.clear()

    # Common formatter for both handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    try:
        import tqdm

        # Use tqdm.write if tqdm is available
        handler = TqdmLoggingHandler()
    except ImportError:
        handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(_LOG_LEVEL)
    handler.setFormatter(formatter)
    
    # Add filter to only allow quickpub logs
    handler.addFilter(QuickpubLogFilter())
    
    logger.addHandler(handler)

def set_log_level(level: int):
    """
    Set the logging level for the root logger and all its handlers.
    
    This function allows end users to dynamically change the log level
    after logging has been set up. It also updates the global _LOG_LEVEL
    constant so that future calls to setup_logging() will use this level.
    
    Args:
        level: Logging level (e.g., logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)
    """
    global _LOG_LEVEL
    _LOG_LEVEL = level
    
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Update all handlers to use the new level
    for handler in logger.handlers:
        handler.setLevel(level)

__all__ = [
    "setup_logging",
    "set_log_level",
    "QuickpubLogFilter"
]
