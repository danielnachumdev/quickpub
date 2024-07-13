import sys
from functools import wraps
from typing import Optional, ContextManager, List, Callable
from danielutils import AttrContext, LayeredCommand, AsciiProgressBar, ColoredText, ProgressBarPool, TemporaryFile

from .managers import PythonManager  # pylint: disable=relative-beyond-top-level
from .structures import AdditionalConfiguration  # pylint: disable=relative-beyond-top-level
from .enforcers import exit_if  # pylint: disable=relative-beyond-top-level

try:
    from danielutils import MultiContext  # type:ignore
except ImportError:
    class MultiContext(ContextManager):  # pylint: disable=missing-class-docstring #type:ignore
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


def validate_dependencies(python_manager: PythonManager, dependencies: List[str], executor: LayeredCommand,
                          env_name: str, err_print_func: Callable) -> None:
    """
    will check if all the dependencies of the package are installed on current env.
    :param python_manager: the manager to use
    :param dependencies: the dependencies to check
    :param executor: the current LayeredCommand executor
    :param env_name: name of the currently checked environment
    :param err_print_func: function to print errors
    :return: None
    """
    if python_manager.exit_on_fail:
        code, out, err = executor("pip list")
        exit_if(code != 0, f"Failed executing 'pip list' at env '{env_name}'", err_func=err_print_func)
        installed = [line.split(' ')[0] for line in out[2:]]
        not_installed = []
        for dep in dependencies:
            if dep not in installed:
                not_installed.append(dep)
        exit_if(not (len(not_installed) == 0),
                f"On env '{env_name}' the following dependencies are not installed: {not_installed}",
                err_func=err_print_func)


def create_progress_bar_pool(config, python_manager) -> ProgressBarPool:
    return ProgressBarPool(
        AsciiProgressBar,
        2,
        individual_options=[
            dict(iterable=python_manager, desc="Envs", total=len(python_manager.requested_envs)),
            dict(iterable=config.runners or [], desc="Runners", total=len(config.runners or [])),
        ]
    )


def create_pool_print_error(pool: ProgressBarPool):
    @wraps(pool.write)
    def func(*args, **kwargs):
        msg = "".join([ColoredText.red("ERROR"), ": ", *args])
        pool.write(msg, **kwargs)

    return func


def qa(package_name: str, config: Optional[AdditionalConfiguration], src_folder_path: Optional[str],
       dependencies: list) -> bool:
    if config is None:
        return True
    result = True
    python_manager = config.python_manager
    is_system_interpreter: bool = False
    if python_manager is None:
        from .managers import SystemInterpreter
        python_manager = SystemInterpreter()
        is_system_interpreter = True
    pool = create_progress_bar_pool(config, python_manager)
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
                    validate_dependencies(python_manager, dependencies, executor, env_name, pool_err)
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
                            raise_on_fail=python_manager.exit_on_fail,
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
                        if python_manager.exit_on_fail:
                            raise e
    return result


__all__ = [
    'qa'
]
