import re
from typing import Dict, List, Union

from ....structures import Dependency, Version

VERSION_REGEX: re.Pattern = re.compile(r"^\d+\.\d+\.\d+$")


def parse_installed_packages_output(
    output_lines: List[str],
) -> Dict[str, Union[str, Dependency]]:
    split_lines = (line.split(" ") for line in output_lines[2:])
    version_tuples = [(s[0], s[-1].strip()) for s in split_lines if s[0]]
    filtered_tuples = [t for t in version_tuples if VERSION_REGEX.match(t[1])]
    currently_installed: Dict[str, Union[str, Dependency]] = {
        name: Dependency(name, "==", Version.from_str(version))
        for name, version in filtered_tuples
    }
    currently_installed.update(
        **{
            name: version
            for name, version in version_tuples
            if not VERSION_REGEX.match(version)
        }
    )
    return currently_installed


__all__ = ["parse_installed_packages_output", "VERSION_REGEX"]
