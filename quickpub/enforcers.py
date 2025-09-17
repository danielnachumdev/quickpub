import logging
from typing import Union, Callable

from danielutils import error

logger = logging.getLogger(__name__)


class ExitEarlyError(Exception):
    """Custom exception raised when early exit conditions are met."""


def exit_if(
        predicate: Union[bool, Callable[[], bool]],
        msg: str,
        *,
        verbose: bool = True,
        err_func: Callable[[str], None] = error
) -> None:
    """
    Exit the program if the given predicate is true.
    
    :param predicate: Boolean value or callable that returns a boolean
    :param msg: Error message to display
    :param verbose: Whether to display the error message
    :param err_func: Function to call for error display
    :raises ExitEarlyError: When the predicate condition is met
    """
    if (isinstance(predicate, bool) and predicate) or (callable(predicate) and predicate()):
        logger.error("Exit condition met: %s", msg)
        if verbose:
            err_func(msg)
        raise ExitEarlyError(msg)


__all__ = [
    "exit_if",
    "ExitEarlyError",
]
