from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class TestingConfiguration:
    name: Literal["unittest", "pytest"]
    tests_folder_path: str = "./tests"
    config_file_path: Optional[str] = None


__all__=[
    "TestingConfiguration",
]