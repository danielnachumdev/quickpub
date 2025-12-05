import logging
from danielutils import RetryExecutor, MultiplicativeBackoff, ConstantBackOffStrategy
from requests import Response
import re
from quickpub.proxy import get  # type: ignore
from quickpub import Version
from ...constraint_enforcer import ConstraintEnforcer

logger = logging.getLogger(__name__)


class PypiRemoteVersionEnforcer(ConstraintEnforcer):
    """Enforces that the new version is greater than the remote PyPI version."""

    _HTTP_FAILED_MESSAGE: str = "Failed to send http request"

    def enforce(self, name: str, version: Version, demo: bool = False, **kwargs) -> None:  # type: ignore
        if demo:
            return

        logger.info(
            "Checking remote version for package '%s' against version '%s'",
            name,
            version,
        )
        url = f"https://pypi.org/simple/{name}/"

        timeout_strategy = MultiplicativeBackoff(2)

        def wrapper() -> Response:
            return get(url, timeout=timeout_strategy.get_backoff())

        executor: RetryExecutor[Response] = RetryExecutor(ConstantBackOffStrategy(1))
        response = executor.execute(wrapper, 5)
        if response is None:
            logger.error("Failed to fetch package information from PyPI for '%s'", name)
            raise self.EXCEPTION_TYPE(self._HTTP_FAILED_MESSAGE)
        html = response.content.decode()

        # Parse version information from href attributes in anchor tags
        # Pattern to match: <a href="...">package-name-version.tar.gz</a>
        # <a href=.*?>(({re.escape(name)})-([^<]+)\.tar\.gz)<\/a><br \/>
        version_pattern = re.compile(
            rf"<a href=.*?>(({re.escape(name)})-([^<]+)\.tar\.gz)<\/a><br \/>"
        )
        matches = version_pattern.findall(html)

        if not matches:
            logger.error("No versions found for package '%s' on PyPI", name)
            raise self.EXCEPTION_TYPE(f"No versions found for package '{name}' on PyPI")

        # Extract all versions and find the latest
        versions = []
        for _, _, version_str in matches:
            try:
                # version_str already contains just the version (e.g., "0.0.0")
                versions.append(Version.from_str(version_str))
            except Exception:
                # Skip invalid version strings
                continue

        if not versions:
            logger.error("No valid versions found for package '%s' on PyPI", name)
            raise self.EXCEPTION_TYPE(
                f"No valid versions found for package '{name}' on PyPI"
            )

        remote_version = max(versions)

        if not version > remote_version:
            logger.error(
                "Version conflict: specified '%s' is not greater than remote '%s'",
                version,
                remote_version,
            )
            raise self.EXCEPTION_TYPE(
                f"Specified version is '{version}' but (remotely available) latest existing is '{remote_version}'"
            )

        logger.info("Version check passed: '%s' > '%s'", version, remote_version)


__all__ = ["PypiRemoteVersionEnforcer"]
