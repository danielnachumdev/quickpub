import re
from pathlib import Path
from typing import List, Union

from .enforcers import ExitEarlyError
from .structures import Version


def normalize_dist_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def find_sdist(
    dist_dir: Union[str, Path],
    name: str,
    version: Union[str, Version],
) -> Path:
    dist_path = Path(dist_dir)
    version_str = str(version)
    candidates: List[Path] = []
    for candidate_name in (name, normalize_dist_name(name)):
        candidate = dist_path / f"{candidate_name}-{version_str}.tar.gz"
        if candidate not in candidates:
            candidates.append(candidate)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise ExitEarlyError(
        f"Could not find sdist for '{name}' version '{version_str}' in '{dist_path}'"
    )


__all__ = ["normalize_dist_name", "find_sdist"]
