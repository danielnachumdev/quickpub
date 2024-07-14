import sys
from typing import Union, Callable

from danielutils import error


def exit_if(predicate: Union[bool, Callable[[], bool]], msg: str, *, verbose: bool = True,
            err_func: Callable[[str], None] = error) -> None:
    if (isinstance(predicate, bool) and predicate) or (callable(predicate) and predicate()):
        if verbose:
            err_func(msg)
        sys.exit(1)


__all__ = [
    "exit_if"
]
