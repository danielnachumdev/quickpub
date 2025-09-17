import logging
import os
from typing import Tuple
import requests
import danielutils

logger = logging.getLogger(__name__)


# need it like this for the testing
def cm(*args, **kwargs) -> Tuple[int, bytes, bytes]:
    """
    Execute a command and return the result.
    
    :param args: Command arguments
    :param kwargs: Additional keyword arguments
    :return: Tuple of (return_code, stdout, stderr)
    """
    logger.debug("Executing command: %s", ' '.join(args))
    result = danielutils.cm(*args, **kwargs)
    logger.debug("Command completed with return code: %d", result[0])
    return result


def os_system(command) -> int:
    """
    Execute a system command.
    
    :param command: Command to execute
    :return: Return code of the command
    """
    logger.debug("Executing system command: %s", command)
    result = os.system(command)
    logger.debug("System command completed with return code: %d", result)
    return result


def get(*args, **kwargs) -> requests.models.Response:
    """
    Make an HTTP GET request.
    
    :param args: Request arguments
    :param kwargs: Additional keyword arguments
    :return: Response object
    """
    logger.debug("Making HTTP GET request to: %s", args[0] if args else 'URL not provided')
    response = requests.get(*args, **kwargs)
    logger.debug("HTTP GET request completed with status code: %d", response.status_code)
    return response


__all__ = [
    "cm",
    'os_system',
    "get"
]
