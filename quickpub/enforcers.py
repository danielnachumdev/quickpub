import sys
from typing import Union, Callable

from danielutils import error


class ExitEarlyError(Exception):
    pass


def exit_if(predicate: Union[bool, Callable[[], bool]], msg: str, *, verbose: bool = True,
            err_func: Callable[[str], None] = error) -> None:
    if (isinstance(predicate, bool) and predicate) or (callable(predicate) and predicate()):
        if verbose:
            err_func(msg)
        raise ExitEarlyError(msg)


__all__ = [
    "exit_if",
    "ExitEarlyError",
]
