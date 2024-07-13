from dataclasses import dataclass
from typing import Optional, List
from ..qa_runners import Runnable
from ..python_managers import PythonManager


@dataclass(frozen=True)
class AdditionalConfiguration:
    python_manager: Optional[PythonManager] = None
    runners: Optional[List[Runnable]] = None


__all__ = [
    'AdditionalConfiguration',
]
