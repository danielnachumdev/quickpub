import os
from typing import Tuple
import danielutils


# need it like this for the testing
def cm(*args, **kwargs) -> Tuple[int, bytes, bytes]:
    return danielutils.cm(*args, **kwargs)


def os_system(command) -> int:
    return os.system(command)


__all__ = [
    "cm",
    'os_system'
]
