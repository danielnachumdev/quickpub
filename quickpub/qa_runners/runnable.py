from abc import ABC, abstractmethod


class Runnable(ABC):
    @abstractmethod
    def run(self, *args, **kwargs) -> float: ...


__all__ = [
    "Runnable"
]
