import sys
from typing import Union, Callable

import requests
from bs4 import BeautifulSoup
from danielutils import directory_exists, get_files, error, file_exists
from .structures import Version
from .proxy import get


def exit_if(predicate: Union[bool, Callable[[], bool]], msg: str) -> None:
    if (isinstance(predicate, bool) and predicate) or (callable(predicate) and predicate()):
        error(msg)
        sys.exit(1)


def enforce_local_correct_version(name: str, version: Version) -> None:
    if directory_exists("./dist"):
        max_version = Version(0, 0, 0)
        for d in get_files("./dist"):
            d = d.removeprefix(f"{name}-").removesuffix(".tar.gz")
            v = Version.from_str(d)
            max_version = max(max_version, v)
        exit_if(
            version <= max_version,
            f"Specified version is '{version}' but (locally available) latest existing is '{max_version}'"
        )


def enforce_remote_correct_version(name: str, version: Version) -> None:
    url = f"https://pypi.org/project/{name}/#history"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return
    # soup = BeautifulSoup(response.text, "html.parser")
    # divs = soup.find_all("div", class_="release")
    # versions = []
    # for div in divs:
    #     ver = div.find("p", class_="release__version").text.strip()
    #     versions.append(ver)
    # pass


def enforce_pypirc_exists() -> None:
    exit_if(
        not file_exists("./.pypirc"),
        "No .pypirc file found"
    )


__all__ = [
    "enforce_local_correct_version",
    "enforce_pypirc_exists"
]
