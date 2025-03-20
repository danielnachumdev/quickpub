import json
import re
import sys
from datetime import datetime
from typing import ContextManager, List, Callable, Tuple, Dict, Union, Any, Literal, Optional
from danielutils import LayeredCommand, ColoredText, TemporaryFile, AsyncWorkerPool, RandomDataGenerator
from danielutils.async_.async_layered_command import AsyncLayeredCommand
from tqdm import tqdm

from .enforcers import ExitEarlyError
from .strategies import PythonProvider, QualityAssuranceRunner  # pylint: disable=relative-beyond-top-level
from .structures import Dependency, Version  # pylint: disable=relative-beyond-top-level
from .enforcers import exit_if  # pylint: disable=relative-beyond-top-level

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


async def global_import_sanity_check(
        package_name: str,
        executor: AsyncLayeredCommand,
        is_system_interpreter: bool,
        env_name: str,
) -> None:
    """
    Will check that importing from the package works as a sanity check.
    :param package_name: Name of the package
    :param executor: the previously ued AsyncLayeredCommand executor
    :param is_system_interpreter: whether or not the system interpreter is used
    :param env_name: The name of the currently tested environment
    :return: None
    """
    p = sys.executable if is_system_interpreter else "python"
    file_name = f"./{RandomDataGenerator().name(15)}__sanity_check_main.py"
    with TemporaryFile(file_name) as f:
        f.writelines([f"from {package_name} import *"])
        cmd = f"{p} {file_name}"
        code, stdout, stderr = await executor(cmd)
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


VERSION_REGEX: re.Pattern = re.compile(r"^\d+\.\d+\.\d+$")


async def validate_dependencies(
        validation_exit_on_fail: bool,
        required_dependencies: List[Dependency],
        executor: AsyncLayeredCommand,
        env_name: str,
) -> None:
    """
    will check if all the dependencies of the package are installed on current env.
    :param validation_exit_on_fail:
    :param required_dependencies: the dependencies to check
    :param executor: the current AsyncLayeredCommand executor
    :param env_name: name of the currently checked environment
    :return: None
    """
    if validation_exit_on_fail:
        code, out, err = await executor("pip list")
        exit_if(code != 0, f"Failed executing 'pip list' at env '{env_name}'",
                err_func=lambda msg: None  # TODO remove
                )
        split_lines = (line.split(' ') for line in out[2:])
        version_tuples = [(s[0], s[-1].strip()) for s in split_lines]
        filtered_tuples = [t for t in version_tuples if VERSION_REGEX.match(t[1])]
        currently_installed: Dict[str, Union[str, Dependency]] = {s[0]: Dependency(s[0], "==", Version.from_str(s[-1]))
                                                                  for s in filtered_tuples}
        currently_installed.update(**{t[0]: t[1] for t in version_tuples if not VERSION_REGEX.match(t[1])})
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

        exit_if(bool(not_installed_properly),
                f"On env '{env_name}' the following dependencies have problems: {(not_installed_properly)}",
                err_func=lambda msg: None  # TODO remove
                )


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
) -> None:
    try:
        await runner.run(
            src_folder_path,
            async_executor,
            use_system_interpreter=is_system_interpreter,
            env_name=env_name
        )
    except ExitEarlyError as e:
        raise e
    except Exception as e:
        # manual_command = async_executor._build_command(runner._build_command(src_folder_path))
        # MyAsyncWorkerPool.log("ERROR", pool=ASYNC_POOL_NAME,
        #                       message=f"Failed running '{runner.__class__.__name__}' on env '{env_name}'. Try manually: '{manual_command}'.",
        #                       exception=e)
        if validation_exit_on_fail:
            raise RuntimeError(e) from e
        return

    is_config_run_success[config_id] = True


class MyAsyncWorkerPool(AsyncWorkerPool):
    @classmethod
    def log(
            self,
            level: Literal["INFO", "WARNING", "ERROR"],
            message: str,
            order: Optional[List[str]] = AsyncWorkerPool.DEFAULT_ORDER_IF_KEY_EXISTS,
            **kwargs
    ) -> None:
        kwargs["level"] = level
        kwargs["message"] = message
        kwargs["timestamp"] = datetime.now().isoformat()
        ordered_kwargs = kwargs
        if order:
            ordered_kwargs = {key: kwargs[key] for key in order if key in kwargs}
            ordered_kwargs.update(kwargs)
        tqdm.write(json.dumps(ordered_kwargs, default=str))


async def qa(
        python_provider: PythonProvider,
        quality_assurance_strategies: List[QualityAssuranceRunner],
        package_name: str,
        src_folder_path: str,
        dependencies: list
) -> bool:
    is_config_run_success.clear()
    from .strategies import DefaultPythonProvider
    is_system_interpreter = isinstance(python_provider, DefaultPythonProvider)
    pool = MyAsyncWorkerPool(ASYNC_POOL_NAME, num_workers=5)
    i = 0
    with AsyncLayeredCommand() as base:
        async for env_name, async_executor in python_provider:
            with async_executor:
                async_executor.prev = base
                await pool.submit(
                    validate_dependencies,
                    args=[
                        python_provider.exit_on_fail,
                        dependencies,
                        async_executor,
                        env_name,
                    ],
                    name=f"Validate dependencies for env '{env_name}'",
                )
                await pool.submit(
                    global_import_sanity_check,
                    args=[
                        package_name,
                        async_executor,
                        is_system_interpreter,
                        env_name,
                    ],
                    name=f"Global Import Sanity Check for env '{env_name}'",
                )
                for runner in quality_assurance_strategies:
                    await pool.submit(
                        run_config,
                        args=[env_name, async_executor, runner, i],
                        kwargs=dict(src_folder_path=src_folder_path,
                                    is_system_interpreter=is_system_interpreter,
                                    validation_exit_on_fail=python_provider.exit_on_fail),
                        name=f"Run config for '{env_name}' + '{runner.__class__.__qualname__}'",
                    )
                    i += 1
    for _ in range(i):
        is_config_run_success.append(False)
    await pool.start()
    await pool.join()

    return all(is_config_run_success)


__all__ = [
    'qa'
]
