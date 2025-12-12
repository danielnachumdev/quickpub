import logging
import re
import sys
import time
from abc import abstractmethod
from datetime import datetime
from typing import (
    ContextManager,
    List,
    Callable,
    Tuple,
    Dict,
    Union,
    Any,
    Literal,
    Optional,
    Protocol,
    runtime_checkable,
)
from danielutils import TemporaryFile, AsyncWorkerPool, RandomDataGenerator
from danielutils.async_.async_layered_command import AsyncLayeredCommand

from .enforcers import ExitEarlyError
from .strategies import (
    PythonProvider,
    QualityAssuranceRunner,
)  # pylint: disable=relative-beyond-top-level
from .structures import Dependency, Version  # pylint: disable=relative-beyond-top-level
from .enforcers import exit_if  # pylint: disable=relative-beyond-top-level
from .worker_pool import WorkerPool

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
    """Protocol for objects that support progress tracking."""

    @abstractmethod
    def update(self, amount: int) -> None:
        """
        Update progress by the given amount.

        :param amount: Amount to update progress by
        """
        ...

    @property
    @abstractmethod
    def total(self) -> int:
        """
        Get the total progress amount.

        :return: Total progress amount
        """
        ...

    @total.setter
    @abstractmethod
    def total(self, amount: int) -> None:
        """
        Set the total progress amount.

        :param amount: Total progress amount
        """
        ...


async def global_import_sanity_check(
    package_name: str,
    executor: AsyncLayeredCommand,
    is_system_interpreter: bool,
    env_name: str,
    task_id: int,
    pbar: Optional[SupportsProgress] = None,
) -> None:
    """
    Will check that importing from the package works as a sanity check.
    :param package_name: Name of the package
    :param executor: the previously ued AsyncLayeredCommand executor
    :param is_system_interpreter: whether or not the system interpreter is used
    :param env_name: The name of the currently tested environment
    :return: None
    """
    logger.info(
        "Running global import sanity check for package '%s' on environment '%s'",
        package_name,
        env_name,
    )
    try:
        p = sys.executable if is_system_interpreter else "python"
        file_name = f"./{RandomDataGenerator().name(15)}__sanity_check_main.py"
        with TemporaryFile(file_name) as f:
            f.writelines([f"from {package_name} import *"])
            cmd = f"{p} {file_name}"
            logger.debug("Executing sanity check command: %s", cmd)
            code, stdout, stderr = await executor(cmd)

            if code != 0:
                logger.error(
                    "Sanity check failed for package '%s' on environment '%s' with return code %d",
                    package_name,
                    env_name,
                    code,
                )
                is_task_run_success[task_id] = False
            else:
                logger.debug(
                    "Sanity check passed for package '%s' on environment '%s'",
                    package_name,
                    env_name,
                )
                is_task_run_success[task_id] = True

            msg = f"Env '{env_name}' failed sanity check."
            if stderr:
                if stderr[0] == "Traceback (most recent call last):":
                    msg += f" Got error '{stderr[-1]}' when tried 'from {package_name} import *'"
            else:
                msg += f" Try manually running the following script 'from {package_name} import *'"
            exit_if(
                code != 0, msg, verbose=True, err_func=lambda msg: None  # TODO remove
            )
    except Exception as e:
        logger.error(
            "Sanity check encountered unexpected error for package '%s' on environment '%s': %s",
            package_name,
            env_name,
            e,
        )
        is_task_run_success[task_id] = False
        raise
    finally:
        if pbar is not None:
            pbar.update(1)


VERSION_REGEX: re.Pattern = re.compile(r"^\d+\.\d+\.\d+$")


async def validate_dependencies(
    validation_exit_on_fail: bool,
    required_dependencies: List[Dependency],
    executor: AsyncLayeredCommand,
    env_name: str,
    task_id: int,
    pbar: Optional[SupportsProgress] = None,
) -> None:
    """
    will check if all the dependencies of the package are installed on current env.
    :param validation_exit_on_fail:
    :param required_dependencies: the dependencies to check
    :param executor: the current AsyncLayeredCommand executor
    :param env_name: name of the currently checked environment
    :return: None
    """
    logger.info("Validating dependencies on environment '%s'", env_name)
    try:
        if validation_exit_on_fail:
            logger.debug("Executing 'pip list' on environment '%s'", env_name)
            code, out, err = await executor("pip list")
            exit_if(
                code != 0,
                f"Failed executing 'pip list' at env '{env_name}'",
                err_func=lambda msg: None,  # TODO remove
            )
            split_lines = (line.split(" ") for line in out[2:])
            version_tuples = [(s[0], s[-1].strip()) for s in split_lines]
            filtered_tuples = [t for t in version_tuples if VERSION_REGEX.match(t[1])]
            currently_installed: Dict[str, Union[str, Dependency]] = {
                s[0]: Dependency(s[0], "==", Version.from_str(s[-1]))
                for s in filtered_tuples
            }
            currently_installed.update(
                **{t[0]: t[1] for t in version_tuples if not VERSION_REGEX.match(t[1])}
            )
            logger.debug("Found %d installed packages", len(currently_installed))

            not_installed_properly: List[Tuple[Dependency, str]] = []
            for req in required_dependencies:
                if req.name not in currently_installed:
                    not_installed_properly.append((req, "dependency not found"))
                else:
                    v = currently_installed[req.name]
                    if isinstance(v, str):
                        not_installed_properly.append(
                            (
                                req,
                                "Version format of dependency is not currently supported by quickpub",
                            )
                        )
                    elif isinstance(v, Dependency):
                        if not req.is_satisfied_by(v.ver):
                            not_installed_properly.append(
                                (req, "Invalid version installed")
                            )

            if not_installed_properly:
                logger.error(
                    "Dependency validation failed on environment '%s': %s",
                    env_name,
                    not_installed_properly,
                )
                is_task_run_success[task_id] = False
            else:
                logger.debug(
                    "Dependency validation passed on environment '%s'", env_name
                )
                is_task_run_success[task_id] = True

            exit_if(
                bool(not_installed_properly),
                f"On env '{env_name}' the following dependencies have problems: {(not_installed_properly)}",
                err_func=lambda msg: None,  # TODO remove
            )
    except Exception as e:
        logger.error(
            "Dependency validation encountered unexpected error on environment '%s': %s",
            env_name,
            e,
        )
        is_task_run_success[task_id] = False
        raise
    finally:
        if pbar is not None:
            pbar.update(1)


# Track all QA tasks (dependencies, sanity checks, QA runners)
is_task_run_success: List[bool] = []


async def run_config(
    env_name: str,
    async_executor: AsyncLayeredCommand,
    runner: QualityAssuranceRunner,
    config_id: int,
    task_id: int,
    *,
    is_system_interpreter: bool,
    validation_exit_on_fail: bool,
    src_folder_path: str,
    pbar: Optional[SupportsProgress] = None,
) -> None:
    """
    Run a QA configuration on a specific environment.

    :param env_name: Name of the environment
    :param async_executor: Async command executor
    :param runner: QA runner instance
    :param config_id: Configuration ID
    :param is_system_interpreter: Whether to use system interpreter
    :param validation_exit_on_fail: Whether to exit on validation failure
    :param src_folder_path: Path to source folder
    :param pbar: Optional progress bar
    """
    logger.info(
        "Running QA config %d on environment '%s' with runner '%s'",
        config_id,
        env_name,
        runner.__class__.__name__,
    )
    try:
        await runner.run(
            src_folder_path,
            async_executor,
            use_system_interpreter=is_system_interpreter,
            env_name=env_name,
        )
        logger.debug(
            "QA config %d completed successfully on environment '%s'",
            config_id,
            env_name,
        )
        is_task_run_success[task_id] = True
    except ExitEarlyError as e:
        logger.error(
            "QA config %d failed on environment '%s': %s", config_id, env_name, e
        )
        is_task_run_success[task_id] = False
        raise e
    except Exception as e:
        logger.error(
            "QA config %d encountered unexpected error on environment '%s': %s",
            config_id,
            env_name,
            e,
        )
        is_task_run_success[task_id] = False
        if validation_exit_on_fail:
            raise RuntimeError(e) from e
        return
    finally:
        if pbar is not None:
            pbar.update(1)


async def qa(
    python_provider: PythonProvider,
    quality_assurance_strategies: List[QualityAssuranceRunner],
    package_name: str,
    src_folder_path: str,
    dependencies: list,
    pbar: Optional[SupportsProgress] = None,
) -> bool:
    """
    Run quality assurance checks on the package.

    :param python_provider: Python environment provider
    :param quality_assurance_strategies: List of QA runners
    :param package_name: Name of the package
    :param src_folder_path: Path to source folder
    :param dependencies: List of dependencies
    :param pbar: Optional progress bar
    :return: True if all QA checks passed, False otherwise
    """
    logger.info(
        "Starting QA process for package '%s' with %d QA strategies",
        package_name,
        len(quality_assurance_strategies),
    )
    qa_start_time = time.perf_counter()
    is_task_run_success.clear()
    from .strategies import DefaultPythonProvider

    is_system_interpreter = isinstance(python_provider, DefaultPythonProvider)

    pool = WorkerPool(ASYNC_POOL_NAME, num_workers=5)
    total = 0
    task_id = 0
    with AsyncLayeredCommand() as base:
        async for env_name, async_executor in python_provider:
            logger.debug("Setting up QA tasks for environment '%s'", env_name)
            with async_executor:
                async_executor.prev = base
                await pool.submit(
                    validate_dependencies,
                    args=[
                        python_provider.exit_on_fail,
                        dependencies,
                        async_executor,
                        env_name,
                        task_id,
                        pbar,
                    ],
                    name=f"Validate dependencies for env '{env_name}'",
                )
                total += 1
                task_id += 1
                await pool.submit(
                    global_import_sanity_check,
                    args=[
                        package_name,
                        async_executor,
                        is_system_interpreter,
                        env_name,
                        task_id,
                        pbar,
                    ],
                    name=f"Global Import Sanity Check for env '{env_name}'",
                )
                total += 1
                task_id += 1
                for runner in quality_assurance_strategies:
                    await pool.submit(
                        run_config,
                        args=[env_name, async_executor, runner, task_id, task_id],
                        kwargs=dict(
                            src_folder_path=src_folder_path,
                            is_system_interpreter=is_system_interpreter,
                            validation_exit_on_fail=python_provider.exit_on_fail,
                            pbar=pbar,
                        ),
                        name=f"Run config for '{env_name}' + '{runner.__class__.__qualname__}'",
                    )
                    total += 1
                    task_id += 1
    if pbar is not None:
        pbar.total = total
    for _ in range(task_id):
        is_task_run_success.append(False)

    logger.info("Starting QA worker pool with %d total tasks", total)
    await pool.start()
    await pool.join()

    # Use unified task tracking for overall success
    success = all(is_task_run_success)
    elapsed = time.perf_counter() - qa_start_time
    logger.info("QA process completed in %.3fs. Success: %s", elapsed, success)
    logger.debug("Task success breakdown: %s", is_task_run_success)
    return success


__all__ = ["qa", "SupportsProgress"]
