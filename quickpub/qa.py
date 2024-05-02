from typing import Optional, ContextManager
from danielutils import AttrContext, LayeredCommand, AsciiProgressBar, file_exists, bprint, subseteq, ColoredText, \
    ProgressBarPool
from .structures import AdditionalConfiguration
from .custom_types import Path
from .enforcers import exit_if
import time

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


def qa(config: Optional[AdditionalConfiguration], src: Optional[Path], dependencies: list) -> None:
    if config is not None:
        if config.runners is not None:
            with MultiContext(
                    AttrContext(LayeredCommand, 'class_flush_stdout', False),
                    AttrContext(LayeredCommand, 'class_flush_stderr', False),
                    AttrContext(LayeredCommand, 'class_raise_on_fail', False)
            ):
                with LayeredCommand() as base:
                    if config.python_manager is None:
                        bar = AsciiProgressBar(config.runners, position=0, total=len(config.runners))
                        for runner in bar:
                            bar.desc = f"Running {runner.__class__.__name__}"
                            runner.run(src, base)
                        return
                pool = ProgressBarPool(
                    AsciiProgressBar,
                    2,
                    individual_options=[
                        dict(iterable=config.python_manager,desc="Envs", total=len(config.python_manager.known_envs)),
                        dict(iterable=config.runners,desc="Runners", total=len(config.runners)),
                    ]
                )
                for name, executor in pool[0]:
                    with executor:
                        executor._prev_instance = base
                        if config.python_manager.exit_on_fail:
                            code, out, err = executor("pip list")
                            exit_if(code != 0, f"Failed executing 'pip list' at env '{name}'")
                            installed = [line.split(' ')[0] for line in out[2:]]
                            not_installed = []
                            for dep in dependencies:
                                if dep not in installed:
                                    not_installed.append(dep)
                            exit_if(not (len(not_installed) == 0),
                                    f"On env '{name}' the following dependencies are not installed: {not_installed}")
                        for runner in pool[1]:
                            try:
                                runner.run(src, executor, verbose=False)
                            except BaseException as e:
                                manual_command = executor._build_command(runner._build_command(src))
                                msg = f"{ColoredText.red('ERROR')}: Failed running '{runner.__class__.__name__}' on env '{name}'. try manually: {manual_command}"
                                pool.write(msg)
                                if config.python_manager.exit_on_fail:
                                    raise e


__all__ = ['qa']
