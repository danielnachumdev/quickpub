import logging
import os
from typing import Tuple, Any
import requests
import danielutils

logger = logging.getLogger(__name__)


# need it like this for the testing
def cm(*args: Any, **kwargs: Any) -> Tuple[int, bytes, bytes]:
    logger.debug("Executing command: %s", " ".join(args))
    result = danielutils.cm(*args, **kwargs)
    logger.debug("Command completed with return code: %d", result[0])
    return result


def os_system(command: str) -> int:
    logger.debug("Executing system command: %s", command)
    result = os.system(command)
    logger.debug("System command completed with return code: %d", result)
    return result


def get(*args: Any, **kwargs: Any) -> requests.models.Response:
    logger.debug(
        "Making HTTP GET request to: %s", args[0] if args else "URL not provided"
    )
    response = requests.get(*args, **kwargs)
    logger.debug(
        "HTTP GET request completed with status code: %d", response.status_code
    )
    return response


__all__ = ["cm", "os_system", "get"]
