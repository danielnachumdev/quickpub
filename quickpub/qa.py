import logging
import re
import sys
from abc import abstractmethod
from datetime import datetime
from typing import ContextManager, List, Callable, Tuple, Dict, Union, Any, Literal, Optional, Protocol, \
    runtime_checkable
from danielutils import TemporaryFile, AsyncWorkerPool, RandomDataGenerator
from danielutils.async_.async_layered_command import AsyncLayeredCommand

from .enforcers import ExitEarlyError
from .strategies import PythonProvider, QualityAssuranceRunner  # pylint: disable=relative-beyond-top-level
from .structures import Dependency, Version  # pylint: disable=relative-beyond-top-level
from .enforcers import exit_if  # pylint: disable=relative-beyond-top-level

logger = logging.getLogger(__name__)

try:
    from danielutils import MultiContext  # type:ignore
except ImportError:
    class MultiContext(ContextManager):  # type: ignore # pylint: disable=missing-class-docstring
        def __init__(self, *contexts: ContextManager):
            self.contexts = contexts

        def __enter__(self):
            for context in self.contexts:
                context.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            for context in self.contexts:
                context.__exit__(exc_type, exc_val, exc_tb)

        def __getitem__(self, index):
            return self.contexts[index]

ASYNC_POOL_NAME: str = "Quickpub QA"


@runtime_checkable
class SupportsProgress(Protocol):
    @abstractmethod
    def update(self, amount: int) -> None:
        ...

    @property
    @abstractmethod
    def total(self) -> int: ...

    @total.setter
    @abstractmethod
    def total(self, amount: int) -> None: ...


async def global_import_sanity_check(
        package_name: str,
        executor: AsyncLayeredCommand,
        is_system_interpreter: bool,
        env_name: str,
        pbar: Optional[SupportsProgress] = None
) -> None:
    """
    Will check that importing from the package works as a sanity check.
    :param package_name: Name of the package
    :param executor: the previously ued AsyncLayeredCommand executor
    :param is_system_interpreter: whether or not the system interpreter is used
    :param env_name: The name of the currently tested environment
    :return: None
    """
    logger.info(f"Running global import sanity check for package '{package_name}' on environment '{env_name}'")
    try:
        p = sys.executable if is_system_interpreter else "python"
        file_name = f"./{RandomDataGenerator().name(15)}__sanity_check_main.py"
        with TemporaryFile(file_name) as f:
            f.writelines([f"from {package_name} import *"])
            cmd = f"{p} {file_name}"
            logger.debug(f"Executing sanity check command: {cmd}")
            code, stdout, stderr = await executor(cmd)
            
            if code != 0:
                logger.error(f"Sanity check failed for package '{package_name}' on environment '{env_name}' with return code {code}")
            
            msg = f"Env '{env_name}' failed sanity check."
            if stderr:
                if stderr[0] == 'Traceback (most recent call last):':
                    msg += f" Got error '{stderr[-1]}' when tried 'from {package_name} import *'"
            else:
                msg += f" Try manually running the following script 'from {package_name} import *'"
            exit_if(
                code != 0, msg,
                verbose=True,
                err_func=lambda msg: None  # TODO remove
            )
        logger.info(f"Sanity check passed for package '{package_name}' on environment '{env_name}'")
    finally:
        if pbar is not None:
            pbar.update(1)


VERSION_REGEX: re.Pattern = re.compile(r"^\d+\.\d+\.\d+$")


async def validate_dependencies(
        validation_exit_on_fail: bool,
        required_dependencies: List[Dependency],
        executor: AsyncLayeredCommand,
        env_name: str,
        pbar: Optional[SupportsProgress] = None
) -> None:
    """
    will check if all the dependencies of the package are installed on current env.
    :param validation_exit_on_fail:
    :param required_dependencies: the dependencies to check
    :param executor: the current AsyncLayeredCommand executor
    :param env_name: name of the currently checked environment
    :return: None
    """
    logger.info(f"Validating dependencies on environment '{env_name}'")
    try:
        if validation_exit_on_fail:
            logger.debug(f"Executing 'pip list' on environment '{env_name}'")
            code, out, err = await executor("pip list")
            exit_if(code != 0, f"Failed executing 'pip list' at env '{env_name}'",
                    err_func=lambda msg: None  # TODO remove
                    )
            split_lines = (line.split(' ') for line in out[2:])
            version_tuples = [(s[0], s[-1].strip()) for s in split_lines]
            filtered_tuples = [t for t in version_tuples if VERSION_REGEX.match(t[1])]
            currently_installed: Dict[str, Union[str, Dependency]] = {
                s[0]: Dependency(s[0], "==", Version.from_str(s[-1]))
                for s in filtered_tuples}
            currently_installed.update(**{t[0]: t[1] for t in version_tuples if not VERSION_REGEX.match(t[1])})
            logger.debug(f"Found {len(currently_installed)} installed packages")
            
            not_installed_properly: List[Tuple[Dependency, str]] = []
            for req in required_dependencies:
                if req.name not in currently_installed:
                    not_installed_properly.append((req, "dependency not found"))
                else:
                    v = currently_installed[req.name]
                    if isinstance(v, str):
                        not_installed_properly.append(
                            (req, "Version format of dependency is not currently supported by quickpub"))
                    elif isinstance(v, Dependency):
                        if not req.is_satisfied_by(v.ver):
                            not_installed_properly.append((req, "Invalid version installed"))

            if not_installed_properly:
                logger.error(f"Dependency validation failed on environment '{env_name}': {not_installed_properly}")
            else:
                logger.info(f"Dependency validation passed on environment '{env_name}'")

            exit_if(bool(not_installed_properly),
                    f"On env '{env_name}' the following dependencies have problems: {(not_installed_properly)}",
                    err_func=lambda msg: None  # TODO remove
                    )
    finally:
        if pbar is not None:
            pbar.update(1)


is_config_run_success: List[bool] = []


async def run_config(
        env_name: str,
        async_executor: AsyncLayeredCommand,
        runner: QualityAssuranceRunner,
        config_id: int,
        *,
        is_system_interpreter: bool,
        validation_exit_on_fail: bool,
        src_folder_path: str,
        pbar: Optional[SupportsProgress] = None
) -> None:
    logger.info(f"Running QA config {config_id} on environment '{env_name}' with runner '{runner.__class__.__name__}'")
    try:
        await runner.run(
            src_folder_path,
            async_executor,
            use_system_interpreter=is_system_interpreter,
            env_name=env_name
        )
        logger.info(f"QA config {config_id} completed successfully on environment '{env_name}'")
    except ExitEarlyError as e:
        logger.error(f"QA config {config_id} failed on environment '{env_name}': {e}")
        raise e
    except Exception as e:
        logger.error(f"QA config {config_id} encountered unexpected error on environment '{env_name}': {e}")
        if validation_exit_on_fail:
            raise RuntimeError(e) from e
        return
    finally:
        if pbar is not None:
            pbar.update(1)
    is_config_run_success[config_id] = True


async def qa(
        python_provider: PythonProvider,
        quality_assurance_strategies: List[QualityAssuranceRunner],
        package_name: str,
        src_folder_path: str,
        dependencies: list,
        pbar: Optional[SupportsProgress] = None
) -> bool:
    logger.info(f"Starting QA process for package '{package_name}' with {len(quality_assurance_strategies)} QA strategies")
    is_config_run_success.clear()
    from .strategies import DefaultPythonProvider
    is_system_interpreter = isinstance(python_provider, DefaultPythonProvider)

    pool = AsyncWorkerPool(ASYNC_POOL_NAME, num_workers=5)
    total = 0
    i = 0
    with AsyncLayeredCommand() as base:
        async for env_name, async_executor in python_provider:
            logger.debug(f"Setting up QA tasks for environment '{env_name}'")
            with async_executor:
                async_executor.prev = base
                await pool.submit(
                    validate_dependencies,
                    args=[
                        python_provider.exit_on_fail,
                        dependencies,
                        async_executor,
                        env_name,
                        pbar
                    ],
                    name=f"Validate dependencies for env '{env_name}'",
                )
                total += 1
                await pool.submit(
                    global_import_sanity_check,
                    args=[
                        package_name,
                        async_executor,
                        is_system_interpreter,
                        env_name,
                        pbar
                    ],
                    name=f"Global Import Sanity Check for env '{env_name}'",
                )
                total += 1
                for runner in quality_assurance_strategies:
                    await pool.submit(
                        run_config,
                        args=[env_name, async_executor, runner, i],
                        kwargs=dict(src_folder_path=src_folder_path,
                                    is_system_interpreter=is_system_interpreter,
                                    validation_exit_on_fail=python_provider.exit_on_fail,
                                    pbar=pbar),
                        name=f"Run config for '{env_name}' + '{runner.__class__.__qualname__}'",
                    )
                    total += 1
                    i += 1
    if pbar is not None:
        pbar.total = total
    for _ in range(i):
        is_config_run_success.append(False)
    
    logger.info(f"Starting QA worker pool with {total} total tasks")
    await pool.start()
    await pool.join()

    success = all(is_config_run_success)
    logger.info(f"QA process completed. Success: {success}")
    return success


__all__ = [
    'qa',
    "SupportsProgress"
]
