import logging
from typing import Union, Callable

from danielutils import error

logger = logging.getLogger(__name__)


class ExitEarlyError(Exception):
    pass


def exit_if(
        predicate: Union[bool, Callable[[], bool]],
        msg: str,
        *,
        verbose: bool = True,
        err_func: Callable[[str], None] = error
) -> None:
    if (isinstance(predicate, bool) and predicate) or (callable(predicate) and predicate()):
        logger.error(f"Exit condition met: {msg}")
        if verbose:
            err_func(msg)
        raise ExitEarlyError(msg)


__all__ = [
    "exit_if",
    "ExitEarlyError",
]
