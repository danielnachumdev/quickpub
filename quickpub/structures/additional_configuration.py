from dataclasses import dataclass
from typing import Optional
from danielutils.versioned_imports import t_list
from ..runnables import Runnable


@dataclass(frozen=True)
class AdditionalConfiguration:
    runners: Optional[t_list[Runnable]]


__all__ = [
    'AdditionalConfiguration',
]
