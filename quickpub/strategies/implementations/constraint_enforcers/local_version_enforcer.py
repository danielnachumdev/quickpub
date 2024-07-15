from danielutils import directory_exists, get_files, get_python_version

from quickpub import Version
from ...constraint_enforcer import ConstraintEnforcer


def _remove_suffix(s: str, suffix: str) -> str:
    """
    This function is needed because str.removesuffix is not implemented in python == 3.8.0
    :param s: string to remove from
    :param suffix: substring to remove
    :return: modified string
    """
    if get_python_version() >= (3, 9):
        return s.removesuffix(suffix)  # type:ignore
    return _remove_prefix(s[::-1], suffix[::-1])[::-1]


def _remove_prefix(s: str, prefix: str) -> str:
    """

    :param s:
    :param prefix:
    :return:
    """
    if get_python_version() >= (3, 9):
        return s.removeprefix(prefix)  # type:ignore

    if s.startswith(prefix):
        return s[len(prefix):]
    return s


class LocalVersionEnforcer(ConstraintEnforcer):
    def enforce(self, name: str, version: Version, demo: bool = False, **kwargs) -> None:  # type: ignore
        if demo:
            return

        if not directory_exists("./dist"):
            return

        prev_builds = get_files("./dist")
        if len(prev_builds) == 0:
            return

        max_local_version = Version(0, 0, 0)
        for d in prev_builds:
            d = _remove_suffix(_remove_prefix(d, f"{name}-"), ".tar.gz")
            v: Version = Version.from_str(d)
            max_local_version = max(max_local_version, v)
        if version <= max_local_version:
            raise self.EXCEPTION_TYPE(
                f"Specified version is '{version}' but (locally available) latest existing is '{max_local_version}'")


__all__ = [
    'LocalVersionEnforcer'
]
