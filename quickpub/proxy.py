import logging
import os
from typing import Tuple
import danielutils
import requests

logger = logging.getLogger(__name__)


# need it like this for the testing
def cm(*args, **kwargs) -> Tuple[int, bytes, bytes]:
    logger.debug(f"Executing command: {' '.join(args)}")
    result = danielutils.cm(*args, **kwargs)
    logger.debug(f"Command completed with return code: {result[0]}")
    return result


def os_system(command) -> int:
    logger.debug(f"Executing system command: {command}")
    result = os.system(command)
    logger.debug(f"System command completed with return code: {result}")
    return result


def get(*args, **kwargs) -> requests.models.Response:
    logger.debug(f"Making HTTP GET request to: {args[0] if args else 'URL not provided'}")
    response = requests.get(*args, **kwargs)
    logger.debug(f"HTTP GET request completed with status code: {response.status_code}")
    return response


__all__ = [
    "cm",
    'os_system',
    "get"
]
