import sys
from typing import Optional, ContextManager, List, Callable
from danielutils import AttrContext, LayeredCommand, AsciiProgressBar, ColoredText, ProgressBarPool, TemporaryFile

from .managers import PythonManager
from .structures import AdditionalConfiguration
from .custom_types import Path
from .enforcers import exit_if

try:
    from danielutils import MultiContext
except ImportError:
    class MultiContext(ContextManager):
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


def global_import_sanity_check(package_name: str, executor: LayeredCommand, is_system_interpreter: bool) -> None:
    p = sys.executable if is_system_interpreter else "python"
    file_name = "./__sanity_check_main.py"
    with TemporaryFile(file_name) as f:
        f.write([f"from {package_name} import *"])
        executor(f"{p} {file_name}", command_raise_on_fail=True)


def validate_dependencies(python_manager: PythonManager, dependencies: List[str], executor: LayeredCommand,
                          env_name: str, print_func: Callable) -> None:
    if python_manager.exit_on_fail:
        code, out, err = executor("pip list")
        exit_if(code != 0, f"Failed executing 'pip list' at env '{env_name}'", err_func=print_func)
        installed = [line.split(' ')[0] for line in out[2:]]
        not_installed = []
        for dep in dependencies:
            if dep not in installed:
                not_installed.append(dep)
        exit_if(not (len(not_installed) == 0),
                f"On env '{env_name}' the following dependencies are not installed: {not_installed}",
                err_func=print_func)


def create_progress_bar_pool(config, python_manager) -> ProgressBarPool:
    return ProgressBarPool(
        AsciiProgressBar,
        2,
        individual_options=[
            dict(iterable=python_manager, desc="Envs", total=len(python_manager.requested_envs)),
            dict(iterable=config.runners or [], desc="Runners", total=len(config.runners or [])),
        ]
    )


def qa(package_name: str, config: Optional[AdditionalConfiguration], src: Optional[Path], dependencies: list) -> None:
    if config is None:
        return
    python_manager = config.python_manager
    is_system_interpreter: bool = False
    if python_manager is None:
        from .managers import SystemInterpreter
        python_manager = SystemInterpreter()
        is_system_interpreter = True
    pool = create_progress_bar_pool(config, python_manager)
    with MultiContext(
            AttrContext(LayeredCommand, 'class_flush_stdout', False),
            AttrContext(LayeredCommand, 'class_flush_stderr', False),
            AttrContext(LayeredCommand, 'class_raise_on_fail', False),
            base := LayeredCommand()
    ):
        for env_name, executor in pool[0]:
            pool[0].desc = f"Env {env_name}"
            pool[0].update(0, refresh=True)
            with executor:
                executor._prev_instance = base
                validate_dependencies(python_manager, dependencies, executor, env_name, pool.write)
                global_import_sanity_check(package_name, executor, is_system_interpreter)
                for runner in pool[1]:
                    pool[1].desc = f"Runner {runner.__class__.__name__}"
                    pool[1].update(0, refresh=True)
                    try:
                        runner.run(
                            src,
                            executor,
                            use_system_interpreter=is_system_interpreter,
                            raise_on_fail=python_manager.exit_on_fail,
                            print_func=pool.write
                        )
                    except BaseException as e:
                        manual_command = executor._build_command(runner._build_command(src))
                        msg = f"{ColoredText.red('ERROR')}: Failed running '{runner.__class__.__name__}' on env '{env_name}'. try manually: '{manual_command}'"
                        pool.write(msg)
                        if python_manager.exit_on_fail:
                            raise e


__all__ = [
    'qa'
]
