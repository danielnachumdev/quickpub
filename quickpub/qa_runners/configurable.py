from abc import ABC
from typing import Optional
from danielutils import file_exists


class Configurable(ABC):
    @property
    def has_config(self) -> bool:
        return self.config_path is not None

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        if self.has_config:
            if not file_exists(self.config_path):
                raise FileNotFoundError(f"Can't find config file {self.config_path}")


__all__ = [
    "Configurable",
]
