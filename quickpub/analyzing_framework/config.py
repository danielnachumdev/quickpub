from dataclasses import dataclass
from typing import Literal, Optional, Union


@dataclass
class Bound:
    operator: Literal["<", "<=", ">", ">="]
    value: float

    def compare_against(self, score: float) -> bool:
        return {
            ">": score > self.value,
            ">=": score >= self.value,
            "<": score < self.value,
            "<=": score <= self.value,
        }[self.operator]

    @staticmethod
    def from_string(s: str) -> 'Bound':
        # the order of iteration matters
        for op in [">=", "<=", ">", "<"]:
            splits = s.split(op)
            if len(splits) == 2:
                return Bound(op, float(splits[-1]))
        raise ValueError("Invalid 'Bound' format")


@dataclass
class StaticAnalyzersConfig:
    name: Literal["pylint", "mypy"]
    executable_path: Optional[str] = None
    config_file_path: Optional[str] = None
    src_folder_path: Optional[str] = None
    bound: Union[str, Bound] = Bound("GE", 0.8)


__all__ = [
    "StaticAnalyzersConfig",
]
