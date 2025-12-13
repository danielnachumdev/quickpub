import logging
from typing import Any

from ...upload_target import UploadTarget

logger = logging.getLogger(__name__)


class GithubUploadTarget(UploadTarget):
    """Upload target implementation for GitHub releases. Commits and pushes changes to the git repository."""

    def upload(self, name: str, version: str, **kwargs: Any) -> None:  # type: ignore[override]
        from quickpub.proxy import cm
        from quickpub.enforcers import exit_if

        logger.info("Starting GitHub upload for version '%s'", version)

        if self.verbose:
            logger.debug("Staging files for Git commit")

        ret, stdout, stderr = cm("git add .")
        if ret != 0:
            logger.error(
                "Git add failed with return code %d: %s",
                ret,
                stderr.decode(encoding="utf8"),
            )
            exit_if(ret != 0, stderr.decode(encoding="utf8"))

        if self.verbose:
            logger.debug(
                "Committing changes with message 'updated to version %s'", version
            )

        ret, stdout, stderr = cm(f'git commit -m "updated to version {version}"')
        if ret != 0:
            logger.error(
                "Git commit failed with return code %d: %s",
                ret,
                stderr.decode(encoding="utf8"),
            )
            exit_if(ret != 0, stderr.decode(encoding="utf8"))

        if self.verbose:
            logger.debug("Pushing changes to GitHub")

        ret, stdout, stderr = cm("git push")
        if ret != 0:
            logger.error(
                "Git push failed with return code %d: %s",
                ret,
                stderr.decode(encoding="utf8"),
            )
            exit_if(ret != 0, stderr.decode(encoding="utf8"))

        logger.info("Successfully uploaded version '%s' to GitHub", version)


__all__ = [
    "GithubUploadTarget",
]
