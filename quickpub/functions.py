import logging
from danielutils import info

from .enforcers import exit_if
from .structures import Version
import quickpub.proxy

logger = logging.getLogger(__name__)


def build(
        *,
        verbose: bool = True
) -> None:
    """
    Build the package distribution.
    
    :param verbose: Whether to display verbose output
    """
    logger.info("Starting build process")
    if verbose:
        info("Creating new distribution...")
        logger.info("Creating new distribution...")

    ret, stdout, stderr = quickpub.proxy.cm("python", "setup.py", "sdist")

    if ret != 0:
        logger.error("Build failed with return code %d: %s", ret, stderr.decode(encoding='utf8'))
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )

    logger.info("Build completed successfully")


def upload(
        *,
        name: str,
        version: Version,
        verbose: bool = True
) -> None:
    """
    Upload the package to PyPI.
    
    :param name: Package name
    :param version: Package version
    :param verbose: Whether to display verbose output
    """
    logger.info("Starting upload process for package '%s' version '%s'", name, version)
    if verbose:
        info("Uploading")
        logger.info("Uploading package to PyPI")

    ret, stdout, stderr = quickpub.proxy.cm("twine", "upload", "--config-file", ".pypirc",
                                            f"dist/{name}-{version}.tar.gz")

    if ret != 0:
        logger.error("Upload failed with return code %d: %s", ret, stderr.decode(encoding='utf8'))
        exit_if(
            ret != 0,
            f"Failed uploading the package to pypi. Try running the following command manually:\n\ttwine upload --config-file .pypirc dist/{name}-{version}.tar.gz"
        )

    logger.info("Successfully uploaded package '%s' version '%s'", name, version)


def commit(
        *,
        version: Version,
        verbose: bool = True
) -> None:
    """
    Commit and push changes to Git repository.
    
    :param version: Package version
    :param verbose: Whether to display verbose output
    """
    logger.info("Starting Git commit process for version '%s'", version)

    if verbose:
        info("Git")
        info("\tStaging")
        logger.info("Staging files for Git commit")

    ret, stdout, stderr = quickpub.proxy.cm("git add .")
    if ret != 0:
        logger.error("Git add failed with return code %d: %s", ret, stderr.decode(encoding='utf8'))
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )

    if verbose:
        info("\tCommitting")
        logger.info("Committing changes with message 'updated to version %s'", version)

    ret, stdout, stderr = quickpub.proxy.cm(f"git commit -m \"updated to version {version}\"")
    if ret != 0:
        logger.error("Git commit failed with return code %d: %s", ret, stderr.decode(encoding='utf8'))
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )

    if verbose:
        info("\tPushing")
        logger.info("Pushing changes to remote repository")

    ret, stdout, stderr = quickpub.proxy.cm("git push")
    if ret != 0:
        logger.error("Git push failed with return code %d: %s", ret, stderr.decode(encoding='utf8'))
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )

    logger.info("Successfully committed and pushed version '%s'", version)


__all__ = [
    "build",
    "upload",
    "commit",
]
