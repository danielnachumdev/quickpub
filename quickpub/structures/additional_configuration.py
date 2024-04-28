from dataclasses import dataclass
from typing import Optional
from ..runnables import Runnable


@dataclass(frozen=True)
class AdditionalConfiguration:
    runners: Optional[list[Runnable]]


__all__ = [
    'AdditionalConfiguration',
]
