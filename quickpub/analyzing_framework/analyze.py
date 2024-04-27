from typing import Optional

from .config import StaticAnalyzersConfig, Bound
from .analyzer_factory import AnalyzerFactory


def analyze(*, analyzer_configurations: Optional[list[StaticAnalyzersConfig]] = None, default_src_path: str) -> None:
    if analyzer_configurations is None:
        return
    from ..enforcers import exit_if
    for config in analyzer_configurations:
        target = config.src_folder_path if config.src_folder_path is not None else default_src_path
        analyzer = AnalyzerFactory.get_analyzer(config.name, args=[config.executable_path, config.config_file_path])
        score = analyzer.analyze(target)

        passed = config.bound.compare_against(score) if isinstance(config.bound, Bound) else Bound.from_string(
            config.bound).compare_against(score)
        exit_if(not passed,
                f"Exiting when analyzing with '{config.name}' because:\n\tscore = {score:.5}\n\tminimum score = {config.bound}")

    __all__ = [
        "analyze"
    ]
