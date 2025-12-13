import logging
import sys
import time
from abc import abstractmethod
from typing import Union, List, Optional, cast, Dict, Tuple
from danielutils import LayeredCommand, get_os, OSType, file_exists
from danielutils.async_.async_layered_command import AsyncLayeredCommand

from quickpub import Bound

logger = logging.getLogger(__name__)


class Configurable:
    @property
    def has_config(self) -> bool:
        return self.config_path is not None

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        if self.has_config:
            logger.debug("Using configuration file: %s", self.config_path)
            if not file_exists(self.config_path):
                logger.error("Configuration file not found: %s", self.config_path)
                raise FileNotFoundError(f"Can't find config file {self.config_path}")


class HasOptionalExecutable:
    PYTHON: str = sys.executable

    @property
    def use_executable(self) -> bool:
        return self.executable_path is not None

    def __init__(self, name: str, executable_path: Optional[str] = None) -> None:
        self.name = name
        self.executable_path = executable_path
        if self.use_executable:
            logger.debug("Using custom executable: %s", self.executable_path)
            if not file_exists(self.executable_path):
                logger.error("Executable not found: %s", self.executable_path)
                raise FileNotFoundError(f"Executable not found {self.executable_path}")
        else:
            logger.debug("Using system executable for: %s", name)

    def get_executable(self, use_system_interpreter: bool = False) -> str:
        if self.use_executable:
            return cast(str, self.executable_path)

        p = self.PYTHON
        if use_system_interpreter:
            p = sys.executable
        return f"{p} -m {self.name}"


SPEICLA_EXIT_CODES: Dict[int, Tuple[str, str]] = {
    -1073741515: (
        "Can't find python in path.",
        "Executing command '{command}' failed with exit code {ret} which in hex is {hex} which corresponds to STATUS_DLL_NOT_FOUND",
    ),
    3221225781: (
        "Can't find python in path.",
        "Executing command '{command}' failed with exit code {ret} which in hex is {hex} which corresponds to STATUS_DLL_NOT_FOUND",
    ),
}


class QualityAssuranceRunner(Configurable, HasOptionalExecutable):
    def __init__(
        self,
        *,
        name: str,
        bound: Union[str, Bound],
        target: Optional[str] = None,
        configuration_path: Optional[str] = None,
        executable_path: Optional[str] = None,
    ) -> None:
        Configurable.__init__(self, configuration_path)
        HasOptionalExecutable.__init__(self, name, executable_path)
        self.bound: Bound = (
            bound if isinstance(bound, Bound) else Bound.from_string(bound)
        )
        self.target = target
        logger.debug(
            "QualityAssuranceRunner '%s' initialized with bound=%s, target=%s",
            name,
            self.bound,
            target,
        )

    @abstractmethod
    def _build_command(
        self, target: str, use_system_interpreter: bool = False
    ) -> str: ...

    @abstractmethod
    def _install_dependencies(self, base: LayeredCommand) -> None: ...

    def _pre_command(self) -> None: ...

    def _post_command(self) -> None: ...

    async def run(
        self,
        target: str,
        executor: AsyncLayeredCommand,
        *,
        verbose: bool = True,  # type: ignore
        use_system_interpreter: bool = False,
        env_name: str,
    ) -> None:
        from quickpub.proxy import os_system  # pylint: disable=import-error
        from quickpub.enforcers import exit_if  # pylint: disable=import-error

        logger.debug(
            "Running %s on environment '%s' with target '%s'",
            self.__class__.__name__,
            env_name,
            target,
        )

        # =====================================
        # IMPORTANT: need to explicitly override it here
        # executor._executor = os_system  # pylint: disable=protected-access #TODO re-fix this for the tests because now this is not working with the async variant
        # =====================================
        command = self._build_command(target, use_system_interpreter)
        logger.debug("Built command: %s", command)

        self._pre_command()
        start_time = time.perf_counter()
        try:
            ret, out, err = await executor(command, command_raise_on_fail=False)
            if ret in SPEICLA_EXIT_CODES:
                title, explanation = SPEICLA_EXIT_CODES[ret]
                unsigned_integer_ret = ret + 2**32
                logger.error("Special exit code %d encountered: %s", ret, title)
                raise RuntimeError(
                    title
                    + "\n\t"
                    + explanation.format(
                        command=command, ret=ret, hex=hex(unsigned_integer_ret)
                    )
                )

            score = self._calculate_score(ret, out + err, verbose=verbose)
            logger.debug(
                "QA runner '%s' scored %.3f (bound: %s)",
                self.__class__.__name__,
                score,
                self.bound,
            )

            if not self.bound.compare_against(score):
                logger.error(
                    "QA runner '%s' failed bound check: %s vs %s",
                    self.__class__.__name__,
                    score,
                    self.bound,
                )

            exit_if(
                not self.bound.compare_against(score),
                f"On env '{env_name}' runner '{self.__class__.__name__}' failed to pass its defined bound. Got a score of {score} but expected {self.bound}",
                verbose=verbose,
                err_func=lambda msg: None,  # TODO remove
            )
        except Exception as e:
            logger.error(
                "QA runner '%s' failed on env '%s': %s",
                self.__class__.__name__,
                env_name,
                e,
            )
            raise RuntimeError(
                f"On env {env_name}, failed to run {self.__class__.__name__}. Try running manually:\n{executor._build_command(command)}",
                e,
            ) from e
        finally:
            elapsed = time.perf_counter() - start_time
            logger.info(
                "QA runner '%s' finished in %.3fs",
                self.__class__.__name__,
                elapsed,
            )
            self._post_command()

    @abstractmethod
    def _calculate_score(
        self, ret: int, command_output: List[str], *, verbose: bool = False
    ) -> float: ...


__all__ = ["QualityAssuranceRunner"]
