from dataclasses import dataclass
from typing import Optional, List
from ..runnables import Runnable


@dataclass(frozen=True)
class AdditionalConfiguration:
    runners: Optional[List[Runnable]]


__all__ = [
    'AdditionalConfiguration',
]
