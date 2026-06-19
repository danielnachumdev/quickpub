from pathlib import Path
from typing import Optional, Tuple

from .strategies.implementations.package_managers.pip_package_manager import (
    PipPackageManager,
)
from .strategies.implementations.package_managers.uv_package_manager import (
    UvPackageManager,
)
from .strategies.implementations.python_providers.default_python_provider import (
    DefaultPythonProvider,
)
from .strategies.implementations.python_providers.uv_python_provider import (
    UvPythonProvider,
)
from .strategies.package_manager import PackageManager
from .strategies.python_provider import PythonProvider


def detect_package_manager(project_root: Path = Path(".")) -> PackageManager:
    if (project_root / "uv.lock").exists():
        return UvPackageManager(project_root=project_root)
    return PipPackageManager()


def resolve_publish_environment(
    project_root: Path = Path("."),
    python_interpreter_provider: Optional[PythonProvider] = None,
    package_manager: Optional[PackageManager] = None,
) -> Tuple[PackageManager, PythonProvider]:
    if package_manager is None:
        package_manager = detect_package_manager(project_root)

    if python_interpreter_provider is None:
        if isinstance(package_manager, UvPackageManager):
            python_interpreter_provider = UvPythonProvider(project_root=project_root)
        else:
            python_interpreter_provider = DefaultPythonProvider()

    return package_manager, python_interpreter_provider


__all__ = ["detect_package_manager", "resolve_publish_environment"]
