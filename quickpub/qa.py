import re
import sys
from functools import wraps
from typing import Optional, ContextManager, List, Callable, Tuple, Dict, Union
from danielutils import AttrContext, LayeredCommand, AsciiProgressBar, ColoredText, ProgressBarPool, TemporaryFile

from quickpub import QualityAssuranceRunner
from .strategies import PythonProvider  # pylint: disable=relative-beyond-top-level
from .structures import Dependency, Version, Bound  # pylint: disable=relative-beyond-top-level
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


def global_import_sanity_check(package_name: str, executor: LayeredCommand, is_system_interpreter: bool,
                               env_name: str, err_print_func) -> None:
    """
    Will check that importing from the package works as a sanity check.
    :param package_name: Name of the package
    :param executor: the previously ued LayeredCommand executor
    :param is_system_interpreter: whether or not the system interpreter is used
    :param env_name: The name of the currently tested environment
    :param err_print_func: the function to print our errors
    :return: None
    """
    p = sys.executable if is_system_interpreter else "python"
    file_name = "./__sanity_check_main.py"
    with TemporaryFile(file_name) as f:
        f.write([f"from {package_name} import *"])
        code, _, _ = executor(f"{p} {file_name}")
        exit_if(code != 0,
                f"Env '{env_name}' failed sanity check. "
                f"Try manually running the following script 'from {package_name} import *'",
                verbose=True, err_func=err_print_func)


VERSION_REGEX: re.Pattern = re.compile(r"^\d+\.\d+\.\d+$")


def validate_dependencies(python_manager: PythonProvider, required_dependencies: List[Dependency],
                          executor: LayeredCommand,
                          env_name: str, err_print_func: Callable) -> None:
    """
    will check if all the dependencies of the package are installed on current env.
    :param python_manager: the manager to use
    :param required_dependencies: the dependencies to check
    :param executor: the current LayeredCommand executor
    :param env_name: name of the currently checked environment
    :param err_print_func: function to print errors
    :return: None
    """
    if python_manager.exit_on_fail:
        code, out, err = executor("pip list")
        exit_if(code != 0, f"Failed executing 'pip list' at env '{env_name}'", err_func=err_print_func)
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
                        (req, "Verion format of dependecy is not currently supported by quickpub"))
                elif isinstance(v, Dependency):
                    if not req.is_satisfied_by(v.ver):
                        not_installed_properly.append((req, "Invalid version installed"))

        exit_if(bool(not_installed_properly),
                f"On env '{env_name}' the following dependencies have problems: {(not_installed_properly)}",
                err_func=err_print_func)


def create_progress_bar_pool(python_version_manager: PythonProvider,
                             quality_assurance_strategies: List[QualityAssuranceRunner]) -> ProgressBarPool:
    return ProgressBarPool(
        AsciiProgressBar,
        2,
        individual_options=[
            dict(
                iterator=python_version_manager,
                desc="Envs",
                total=len(python_version_manager.requested_envs)
            ),
            dict(
                iterator=quality_assurance_strategies or [],
                desc="Runners",
                total=len(quality_assurance_strategies or [])
            ),
        ]
    )


def create_pool_print_error(pool: ProgressBarPool):
    @wraps(pool.write)
    def func(*args, **kwargs):
        msg = "".join([ColoredText.red("ERROR"), ": ", *args])
        pool.write(msg, **kwargs)

    return func


def qa(
        python_version_manager: PythonProvider,
        quality_assurance_strategies: List[QualityAssuranceRunner],
        package_name: str,
        src_folder_path: Optional[str],
        dependencies: list
) -> bool:
    from .strategies import DefaultInterpreterProvider
    result = True
    if python_version_manager is None:
        python_version_manager = DefaultInterpreterProvider()
    is_system_interpreter = isinstance(python_version_manager, DefaultInterpreterProvider)
    pool = create_progress_bar_pool(python_version_manager, quality_assurance_strategies)
    pool_err = create_pool_print_error(pool)
    with MultiContext(
            AttrContext(LayeredCommand, 'class_flush_stdout', False),
            AttrContext(LayeredCommand, 'class_flush_stderr', False),
            AttrContext(LayeredCommand, 'class_raise_on_fail', False),
            base := LayeredCommand()
    ):
        for env_name, executor in pool[0]:
            pool[0].desc = f"Env '{env_name}'"
            pool[0].update(0, refresh=True)
            with executor:
                executor._prev_instance = base
                try:
                    validate_dependencies(python_version_manager, dependencies, executor, env_name, pool_err)
                except SystemExit:
                    result = False
                    continue
                try:
                    global_import_sanity_check(package_name, executor, is_system_interpreter, env_name, pool_err)
                except SystemExit:
                    result = False
                    continue
                for runner in pool[1]:
                    pool[1].desc = f"Runner '{runner.__class__.__name__}'"
                    pool[1].update(0, refresh=True)
                    try:
                        runner.run(
                            src_folder_path,
                            executor,
                            use_system_interpreter=is_system_interpreter,
                            print_func=pool_err,
                            env_name=env_name
                        )
                    except SystemExit:
                        result = False
                        continue
                    except Exception as e:
                        result = False
                        manual_command = executor._build_command(runner._build_command(src_folder_path))
                        pool_err(
                            f"Failed running '{runner.__class__.__name__}' on env '{env_name}'. "
                            f"Try manually: '{manual_command}'.")
                        pool.write(f"\tCaused by '{e.__cause__ or e}'")
                        if python_version_manager.exit_on_fail:
                            raise RuntimeError() from e
    return result


__all__ = [
    'qa'
]
