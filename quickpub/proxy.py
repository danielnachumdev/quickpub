import os
from typing import Tuple
import danielutils
import requests


# need it like this for the testing
def cm(*args, **kwargs) -> Tuple[int, bytes, bytes]:
    return danielutils.cm(*args, **kwargs)


def os_system(command) -> int:
    return os.system(command)


def get(*args, **kwargs):
    return requests.get(*args, **kwargs)


__all__ = [
    "cm",
    'os_system',
    "get"
]
