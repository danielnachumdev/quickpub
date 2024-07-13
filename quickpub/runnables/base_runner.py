from abc import abstractmethod
from typing import Optional, Union, List

from danielutils import LayeredCommand

from .has_optional_executable import HasOptionalExecutable
from .runnable import Runnable
from .configurable import Configurable
from ..structures import Bound
from ..proxy import os_system


class BaseRunner(Runnable, Configurable, HasOptionalExecutable):

    def __init__(self, *, name: str, bound: Union[str, Bound], target: Optional[str] = None,
                 configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None, auto_install: bool = False) -> None:
        Configurable.__init__(self, configuration_path)
        HasOptionalExecutable.__init__(self, name, executable_path)
        self.bound: Bound = bound if isinstance(bound, Bound) else Bound.from_string(bound)
        self.target = target

    @abstractmethod
    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        ...

    @abstractmethod
    def _install_dependencies(self, base: LayeredCommand) -> None:
        ...

    def _pre_command(self) -> None:
        pass

    def _post_command(self) -> None:
        pass

    def run(self, target: str, executor: LayeredCommand, *_, verbose: bool = True,  # type: ignore
            use_system_interpreter: bool = False, raise_on_fail: bool = False, print_func, env_name: str) -> None:
        # =====================================
        # IMPORTANT: need to explicitly override it here
        executor._executor = os_system
        # =====================================
        command = self._build_command(target, use_system_interpreter)
        self._pre_command()
        try:
            ret, out, err = executor(command, command_raise_on_fail=raise_on_fail)
            score = self._calculate_score(ret, "".join(out + err).splitlines(), verbose=verbose)
            from ..enforcers import exit_if
            exit_if(not self.bound.compare_against(score),
                    f"On env '{env_name}' runner '{self.__class__.__name__}' failed to pass it's defined bound. Got a score of {score} but expected {self.bound}",
                    verbose=verbose, err_func=print_func)
        except Exception as e:
            raise RuntimeError(
                f"On env {env_name}, failed to run {self.__class__.__name__}. Try running manually:\n{executor._build_command(command)}") from e
        finally:
            self._post_command()

    @abstractmethod
    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        ...


__all__ = [
    "BaseRunner"
]
