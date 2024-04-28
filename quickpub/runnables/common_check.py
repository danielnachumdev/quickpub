import os
from abc import abstractmethod
from typing import Optional, Union

from danielutils import file_exists, cm, info, get_current_working_directory, set_current_working_directory

from .has_optional_executable import HasOptionalExecutable
from .runnable import Runnable
from .configurable import Configurable
from ..structures import Bound


class CommonCheck(Runnable, Configurable, HasOptionalExecutable):

    def __init__(self, name: str, bound: Union[str, Bound], target: Optional[str] = None,
                 configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
        Configurable.__init__(self, configuration_path)
        HasOptionalExecutable.__init__(self, name, executable_path)
        self.bound: Bound = bound if isinstance(bound, Bound) else Bound.from_string(bound)
        self.target = target

    def _build_command(self, target: str) -> str:
        command: str = self.get_executable()
        if self.has_config:
            command += f" --rcfile {self.config_path}"
        command += f" {target}"
        return command

    @abstractmethod
    def _pre_command(self):
        ...

    @abstractmethod
    def _post_command(self):
        ...

    def run(self, target: str, *_) -> None:
        command = self._build_command(target)
        info(f"Running {self.name}")
        self._pre_command()
        try:
            ret, out, err = cm(command)
            score = self._calculate_score(ret, b"".join([out, err]).decode("utf-8").splitlines())
            from ..enforcers import exit_if
            exit_if(not self.bound.compare_against(score), f"{self.name} failed to pass it's defined bound")
        finally:
            self._post_command()


@abstractmethod
def _calculate_score(self, ret: int, command_output: list[str]) -> float: ...


__all__ = [
    "CommonCheck"
]
