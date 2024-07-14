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


from typing import Optional, Union, List
from abc import abstractmethod


class QualityAssuranceRunner(Configurable, HasOptionalExecutable):
    """
    QualityAssuranceRunner is an abstract base class that handles the execution of quality assurance
    processes. It extends Configurable and HasOptionalExecutable to incorporate configuration and
    optional executable handling functionalities.

    :param name: The name of the QA runner.
    :param bound: The bound representing acceptable limits, either as a string or a Bound object.
    :param target: The target to be tested, optional.
    :param configuration_path: The path to the configuration file, optional.
    :param executable_path: The path to the executable, optional.

    Attributes:
        bound (Bound): The bound object that represents the acceptable limits for the QA process.
        target (Optional[str]): The target to be tested.
    """

    def __init__(
            self, *,
            name: str,
            bound: Union[str, Bound],
            target: Optional[str] = None,
            configuration_path: Optional[str] = None,
            executable_path: Optional[str] = None
    ) -> None:
        """
        Initializes the QualityAssuranceRunner with the given parameters.

        :param name: The name of the QA runner.
        :param bound: The bound representing acceptable limits, either as a string or a Bound object.
        :param target: The target to be tested, optional.
        :param configuration_path: The path to the configuration file, optional.
        :param executable_path: The path to the executable, optional.
        """
        Configurable.__init__(self, configuration_path)
        HasOptionalExecutable.__init__(self, name, executable_path)
        self.bound: Bound = bound if isinstance(bound, Bound) else Bound.from_string(bound)
        self.target = target

    @abstractmethod
    def _build_command(self, target: str, use_system_interpreter: bool = False) -> str:
        """
        Builds the command to be executed for the QA process.

        :param target: The target to be tested.
        :param use_system_interpreter: Whether to use the system interpreter, default is False.
        :return: The command to be executed as a string.
        """

    @abstractmethod
    def _install_dependencies(self, base: LayeredCommand) -> None:
        """
        Installs the necessary dependencies for the QA process.

        :param base: The base LayeredCommand object for executing commands.
        """

    def _pre_command(self) -> None:
        """
        Hook method to be executed before running the main command.
        Can be overridden by subclasses.
        """
        pass

    def _post_command(self) -> None:
        """
        Hook method to be executed after running the main command.
        Can be overridden by subclasses.
        """
        pass

    def run(self, target: str, executor: LayeredCommand, *, verbose: bool = True,  # type: ignore
            use_system_interpreter: bool = False, print_func, env_name: str) -> None:
        """
        Runs the QA process on the specified target.

        :param target: The target to be tested.
        :param executor: The executor object to run the command.
        :param verbose: Whether to output verbose logs, default is True.
        :param use_system_interpreter: Whether to use the system interpreter, default is False.
        :param print_func: The function to use for printing output.
        :param env_name: The name of the environment in which the QA runner is executed.
        """
        from quickpub.proxy import os_system  # pylint: disable=import-error
        from quickpub.enforcers import exit_if  # pylint: disable=import-error
        # =====================================
        # IMPORTANT: need to explicitly override it here
        executor._executor = os_system  # pylint: disable=protected-access
        # =====================================
        command = self._build_command(target, use_system_interpreter)
        self._pre_command()
        try:
            ret, out, err = executor(command, command_raise_on_fail=False)
            score = self._calculate_score(ret, "".join(out + err).splitlines(), verbose=verbose)
            exit_if(not self.bound.compare_against(score),
                    f"On env '{env_name}' runner '{self.__class__.__name__}' failed to pass its defined bound. Got a score of {score} but expected {self.bound}",
                    verbose=verbose, err_func=print_func)
        except Exception as e:
            raise RuntimeError(
                f"On env {env_name}, failed to run {self.__class__.__name__}. Try running manually:\n{executor._build_command(command)}") from e
        finally:
            self._post_command()

    @abstractmethod
    def _calculate_score(self, ret: int, command_output: List[str], *, verbose: bool = False) -> float:
        """
        Calculates the score based on the command's return code and output.

        :param ret: The return code of the executed command.
        :param command_output: The output of the command as a list of strings.
        :param verbose: Whether to output verbose logs, default is False.
        :return: The calculated score as a float.
        """
        ...


__all__ = [
    "QualityAssuranceRunner"
]
