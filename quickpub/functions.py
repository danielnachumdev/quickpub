import logging
import sys
from typing import Optional, Literal
from danielutils import info

from .enforcers import exit_if
from .structures import Version
import quickpub.proxy

logger = logging.getLogger(__name__)


def build(
        *,
        verbose: bool = True
) -> None:
    logger.info("Starting build process")
    if verbose:
        info("Creating new distribution...")
        logger.info("Creating new distribution...")
    
    ret, stdout, stderr = quickpub.proxy.cm("python", "setup.py", "sdist")
    
    if ret != 0:
        logger.error(f"Build failed with return code {ret}: {stderr.decode(encoding='utf8')}")
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
    logger.info(f"Starting upload process for package '{name}' version '{version}'")
    if verbose:
        info("Uploading")
        logger.info("Uploading package to PyPI")
    
    ret, stdout, stderr = quickpub.proxy.cm("twine", "upload", "--config-file", ".pypirc",
                                            f"dist/{name}-{version}.tar.gz")
    
    if ret != 0:
        logger.error(f"Upload failed with return code {ret}: {stderr.decode(encoding='utf8')}")
        exit_if(
            ret != 0,
            f"Failed uploading the package to pypi. Try running the following command manually:\n\ttwine upload --config-file .pypirc dist/{name}-{version}.tar.gz"
        )
    
    logger.info(f"Successfully uploaded package '{name}' version '{version}'")


def commit(
        *,
        version: Version,
        verbose: bool = True
) -> None:
    logger.info(f"Starting Git commit process for version '{version}'")
    
    if verbose:
        info("Git")
        info("\tStaging")
        logger.info("Staging files for Git commit")
    
    ret, stdout, stderr = quickpub.proxy.cm("git add .")
    if ret != 0:
        logger.error(f"Git add failed with return code {ret}: {stderr.decode(encoding='utf8')}")
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )
    
    if verbose:
        info("\tCommitting")
        logger.info(f"Committing changes with message 'updated to version {version}'")
    
    ret, stdout, stderr = quickpub.proxy.cm(f"git commit -m \"updated to version {version}\"")
    if ret != 0:
        logger.error(f"Git commit failed with return code {ret}: {stderr.decode(encoding='utf8')}")
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )
    
    if verbose:
        info("\tPushing")
        logger.info("Pushing changes to remote repository")
    
    ret, stdout, stderr = quickpub.proxy.cm("git push")
    if ret != 0:
        logger.error(f"Git push failed with return code {ret}: {stderr.decode(encoding='utf8')}")
        exit_if(
            ret != 0,
            stderr.decode(encoding="utf8")
        )
    
    logger.info(f"Successfully committed and pushed version '{version}'")


__all__ = [
    "build",
    "upload",
    "commit",
]
