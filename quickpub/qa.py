from typing import Optional, ContextManager
from danielutils import AttrContext, LayeredCommand, AsciiProgressBar, ColoredText, ProgressBarPool, TemporaryFile, \
    ProgressBar

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


def global_import_sanity_check(package_name: str, python_manager, dependencies) -> None:
    main_file_name = "./__temp_main.py"
    all_dependencies = " ".join(dependencies)
    with TemporaryFile(main_file_name) as main:
        main.write([f"from {package_name} import *"])
        bar = AsciiProgressBar(python_manager, position=0, total=len(python_manager))
        for name, layered_command in python_manager:
            bar.desc = f"Running '{name}'"
            bar.update(0)
            with MultiContext(
                    AttrContext(layered_command, "_instance_flush_stdout", False),
                    AttrContext(layered_command, "_instance_flush_stderr", False),
            ):
                with layered_command as base:
                    if python_manager.auto_install_dependencies:
                        pip_command = f"pip install -U {all_dependencies}"
                        code, _, _ = base(pip_command)
                        exit_if(
                            code != 0,
                            f"Failed installing dependencies, try manually with '{base._build_command(pip_command)}",
                            err_func=bar.write
                        )
                    code, _, _ = base(f"python {main_file_name}", command_raise_on_fail=False)
                    exit_if(code != 0,
                            f"Global import failed. try manually with '{base._build_command()}' and then 'from {package_name} import *'")
            bar.update(1)


def validate_dependencies(python_manager, dependencies, executor, name):
    if python_manager.exit_on_fail:
        code, out, err = executor("pip list")
        exit_if(code != 0, f"Failed executing 'pip list' at env '{name}'")
        installed = [line.split(' ')[0] for line in out[2:]]
        not_installed = []
        for dep in dependencies:
            if dep not in installed:
                not_installed.append(dep)
        exit_if(not (len(not_installed) == 0),
                f"On env '{name}' the following dependencies are not installed: {not_installed}")


def create_progress_bar_pool(config, python_manager):
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
        for name, executor in pool[0]:
            with executor:
                executor._prev_instance = base
                validate_dependencies(python_manager, dependencies, executor, name)
                for runner in pool[1]:
                    try:
                        runner.run(src, executor, verbose=is_system_interpreter, use_system_interpreter=is_system_interpreter)
                    except BaseException as e:
                        manual_command = executor._build_command(runner._build_command(src))
                        msg = f"{ColoredText.red('ERROR')}: Failed running '{runner.__class__.__name__}' on env '{name}'. try manually: '{manual_command}'"
                        pool.write(msg)
                        if python_manager.exit_on_fail:
                            raise e

                # global_import_sanity_check(package_name, python_manager, dependencies)


__all__ = [
    'qa'
]
