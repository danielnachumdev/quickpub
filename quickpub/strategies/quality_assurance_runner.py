import sys
from abc import abstractmethod
from typing import Union, List, Optional, cast
from danielutils import LayeredCommand, get_os, OSType, file_exists

from quickpub import Bound


class Configurable:
    @property
    def has_config(self) -> bool:
        return self.config_path is not None

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        if self.has_config:
            if not file_exists(self.config_path):
                raise FileNotFoundError(f"Can't find config file {self.config_path}")


class HasOptionalExecutable:
    PYTHON: str = "python" if get_os() == OSType.WINDOWS else "python3"

    @property
    def use_executable(self) -> bool:
        return self.executable_path is not None

    def __init__(self, name, executable_path: Optional[str] = None) -> None:
        self.name = name
        self.executable_path = executable_path
        if self.use_executable:
            if not file_exists(self.executable_path):
                raise FileNotFoundError(f"Executable not found {self.executable_path}")

    def get_executable(self, use_system_interpreter: bool = False) -> str:
        if self.use_executable:
            return cast(str, self.executable_path)

        p = self.PYTHON
        if use_system_interpreter:
            p = sys.executable
        return f"{p} -m {self.name}"


class QualityAssuranceRunner(Configurable, HasOptionalExecutable):

    def __init__(self, *, name: str, bound: Union[str, Bound], target: Optional[str] = None,
                 configuration_path: Optional[str] = None,
                 executable_path: Optional[str] = None) -> None:
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
        from quickpub.proxy import os_system
        from quickpub.enforcers import exit_if
        executor._executor = os_system
        # =====================================
        command = self._build_command(target, use_system_interpreter)
        self._pre_command()
        try:
            ret, out, err = executor(command, command_raise_on_fail=False)
            score = self._calculate_score(ret, "".join(out + err).splitlines(), verbose=verbose)
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
    "QualityAssuranceRunner"
]
