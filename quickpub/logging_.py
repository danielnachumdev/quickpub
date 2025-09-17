import logging
import sys

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

def setup_logging(level: int = logging.INFO):
    """
    Set up logging with appropriate handler based on tqdm availability.

    If tqdm is installed, uses tqdm.write for output to avoid conflicts with progress bars.
    If tqdm is not installed, uses a standard StreamHandler to stdout.

    Args:
        level: Logging level (default: logging.INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger()
    logger.setLevel(level)

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
    handler.setLevel(level)
    handler.setFormatter(formatter)
    
    # Add filter to only allow quickpub logs
    handler.addFilter(QuickpubLogFilter())
    
    logger.addHandler(handler)



__all__ = [
    "setup_logging",
    "QuickpubLogFilter"
]
