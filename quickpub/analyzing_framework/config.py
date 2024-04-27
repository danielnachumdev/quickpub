from dataclasses import dataclass
from typing import Literal, Optional, Union
from ..structures.bound import Bound


@dataclass
class StaticAnalyzersConfig:
    name: Literal["pylint", "mypy"]
    executable_path: Optional[str] = None
    config_file_path: Optional[str] = None
    src_folder_path: Optional[str] = None
    bound: Union[str, Bound] = Bound(">=", 0.8)


__all__ = [
    "StaticAnalyzersConfig",
]
