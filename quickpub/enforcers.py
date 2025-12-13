import logging
from typing import Union, Callable


logger = logging.getLogger(__name__)


class ExitEarlyError(Exception):
    pass


def exit_if(
    predicate: Union[bool, Callable[[], bool]],
    msg: str,
) -> None:
    if (isinstance(predicate, bool) and predicate) or (
        callable(predicate) and predicate()
    ):
        logger.error("Exit condition met: %s", msg)
        raise ExitEarlyError(msg)


__all__ = [
    "exit_if",
    "ExitEarlyError",
]
