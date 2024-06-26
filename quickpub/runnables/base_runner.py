from abc import abstractmethod
from typing import Optional, Union, List

from danielutils import cm, info, LayeredCommand

from .has_optional_executable import HasOptionalExecutable
from .runnable import Runnable
from .configurable import Configurable
from ..structures import Bound
from ..proxy import os_system


class BaseRunner(Runnable, Configurable, HasOptionalExecutable):

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

    def _pre_command(self) -> None:
        pass

    def _post_command(self) -> None:
        pass

    def run(self, target: str, executor: LayeredCommand, *_, verbose: bool = True) -> None:
        # need to explicitly override it here
        executor._executor = os_system
        command = self._build_command(target)
        # info(f"Running {self.name}")
        self._pre_command()
        try:
            ret, out, err = executor(command)
            score = self._calculate_score(ret, "".join(out + err).splitlines(), verbose=verbose)
            from ..enforcers import exit_if
            exit_if(not self.bound.compare_against(score), f"{self.name} failed to pass it's defined bound",
                    verbose=verbose)
        except BaseException as e:
            raise RuntimeError(
                f"Failed to run {self.name}, try running manually:\n{executor._build_command(command)}") from e
        finally:
            self._post_command()

    @abstractmethod
    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        ...


__all__ = [
    "BaseRunner"
]
