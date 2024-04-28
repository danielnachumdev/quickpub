from abc import abstractmethod
from typing import Optional, Union, List

from danielutils import cm, info

from .has_optional_executable import HasOptionalExecutable
from .runnable import Runnable
from .configurable import Configurable
from ..structures import Bound


class CommonCheck(Runnable, Configurable, HasOptionalExecutable):

    def __init__(self, *, name: str, bound: Union[str, Bound], target: Optional[str] = None,
                 configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        Configurable.__init__(self, configuration_path)
        HasOptionalExecutable.__init__(self, name, executable_path)
        self.bound: Bound = bound if isinstance(bound, Bound) else Bound.from_string(bound)
        self.target = target

    @abstractmethod
    def _build_command(self, target: str) -> str:
        ...

    def _pre_command(self):
        pass

    def _post_command(self):
        pass

    def run(self, target: str, *_) -> None:
        command = self._build_command(target)
        info(f"Running {self.name}")
        self._pre_command()
        try:
            ret, out, err = cm(command)
            score = self._calculate_score(ret, b"".join([out, err]).decode("utf-8").splitlines())
            from ..enforcers import exit_if
            exit_if(not self.bound.compare_against(score), f"{self.name} failed to pass it's defined bound")
        except Exception as e:
            raise RuntimeError(
                f"Failed to run {self.name}, try running manually:\n{self._build_command('TARGET')}") from e
        finally:
            self._post_command()


@abstractmethod
def _calculate_score(self, ret: int, command_output: List[str]) -> float: ...


__all__ = [
    "CommonCheck"
]
