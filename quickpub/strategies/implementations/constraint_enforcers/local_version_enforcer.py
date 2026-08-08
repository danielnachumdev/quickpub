import logging
from typing import Any, Optional

from danielutils import directory_exists, get_files

from quickpub import Version
from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


def _version_from_dist_filename(name: str, filename: str) -> Optional[Version]:
    prefix = f"{name}-"
    if not filename.startswith(prefix):
        return None
    if filename.endswith(".tar.gz"):
        version_str = filename[len(prefix) : -len(".tar.gz")]
    elif filename.endswith(".whl"):
        version_str = filename[len(prefix) : -len(".whl")].split("-")[0]
    else:
        return None
    try:
        return Version.from_str(version_str)
    except ValueError:
        return None


class LocalVersionEnforcer(ConstraintEnforcer):
    """Enforces that the new version is greater than the highest version found in the local dist directory."""

    def enforce(
        self, name: str, version: Version, demo: bool = False, **kwargs: Any
    ) -> None:  # type: ignore[override]
        if demo:
            return

        logger.info(
            "Checking local version for package '%s' against version '%s'",
            name,
            version,
        )

        if not directory_exists("./dist"):
            logger.info("No dist directory found, skipping local version check")
            return

        prev_builds = get_files("./dist")
        if len(prev_builds) == 0:
            logger.info("No previous builds found in dist directory")
            return

        max_local_version = Version(0, 0, 0)
        found_artifact = False
        for filename in prev_builds:
            parsed = _version_from_dist_filename(name, filename)
            if parsed is None:
                continue
            found_artifact = True
            max_local_version = max(max_local_version, parsed)

        if not found_artifact:
            logger.info("No sdist or wheel artifacts found in dist directory")
            return

        if version <= max_local_version:
            logger.error(
                "Version conflict: specified '%s' is not greater than local '%s'",
                version,
                max_local_version,
            )
            raise self.EXCEPTION_TYPE(
                f"Specified version is '{version}' but (locally available) latest existing is '{max_local_version}'"
            )

        logger.info(
            "Local version check passed: '%s' > '%s'", version, max_local_version
        )


__all__ = ["LocalVersionEnforcer"]
