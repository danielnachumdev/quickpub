from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class StaticAnalyzersConfig:
    name: Literal["pylint", "mypy"]
    executable_path: Optional[str] = None
    config_file_path: Optional[str] = None
    src_folder_path: Optional[str] = None
    min_allowed_score: float = 0.8


__all__ = [
    "StaticAnalyzersConfig",
]
