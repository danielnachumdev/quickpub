import logging
import sys


class QuickpubFilter(logging.Filter):
    """
    Filter that only allows logs from the quickpub package to pass through.
    """
    
    def filter(self, record):
        # Check if the logger name starts with 'quickpub'
        return record.name.startswith('quickpub')


def setup_test_logging():
    """
    Set up logging for tests with a stdout stream handler.
    This allows logs to be visible during test execution.
    Only logs from the quickpub package will be shown.
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Set logging level to DEBUG to see all logs during testing
    logger.setLevel(logging.DEBUG)
    
    # Create a stream handler that outputs to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    
    # Add the quickpub filter to only show quickpub logs
    quickpub_filter = QuickpubFilter()
    stream_handler.addFilter(quickpub_filter)
    
    # Create a formatter for the logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    stream_handler.setFormatter(formatter)
    
    # Add the handler to the root logger
    logger.addHandler(stream_handler)
    
    # Also configure the quickpub loggers specifically
    quickpub_logger = logging.getLogger('quickpub')
    quickpub_logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to avoid duplicate logs
    quickpub_logger.propagate = True


# Set up logging when the tests module is imported
setup_test_logging()
