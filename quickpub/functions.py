import sys
from typing import Optional, Literal
from danielutils import info

from .enforcers import exit_if
from .structures import Version
import quickpub.proxy


def build(
        *,
        verbose: bool = True
) -> None:
    if verbose:
        info("Creating new distribution...")
    ret, stdout, stderr = quickpub.proxy.cm("python", "setup.py", "sdist")
    exit_if(
        ret != 0,
        stderr.decode(encoding="utf8")
    )


def upload(
        *,
        name: str,
        version: Version,
        verbose: bool = True
) -> None:
    if verbose:
        info("Uploading")
    ret, stdout, stderr = quickpub.proxy.cm("twine", "upload", "--config-file", ".pypirc",
                                            f"dist/{name}-{version}.tar.gz")
    exit_if(
        ret != 0,
        f"Failed uploading the package to pypi. Try running the following command manually:\n\ttwine upload --config-file .pypirc dist/{name}-{version}.tar.gz"
    )


def commit(
        *,
        version: Version,
        verbose: bool = True
) -> None:
    if verbose:
        info("Git")
        info("\tStaging")
    ret, stdout, stderr = quickpub.proxy.cm("git add .")
    exit_if(
        ret != 0,
        stderr.decode(encoding="utf8")
    )
    if verbose:
        info("\tCommitting")
    ret, stdout, stderr = quickpub.proxy.cm(f"git commit -m \"updated to version {version}\"")
    exit_if(
        ret != 0,
        stderr.decode(encoding="utf8")
    )
    if verbose:
        info("\tPushing")
    ret, stdout, stderr = quickpub.proxy.cm("git push")
    exit_if(
        ret != 0,
        stderr.decode(encoding="utf8")
    )


__all__ = [
    "build",
    "upload",
    "commit",
]
