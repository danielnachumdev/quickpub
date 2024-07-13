import sys
from typing import Union, Callable

from danielutils import directory_exists, get_files, error, file_exists, get_python_version
from .structures import Version


def exit_if(predicate: Union[bool, Callable[[], bool]], msg: str, *, verbose: bool = True,
            err_func: Callable[[str], None] = error) -> None:
    if (isinstance(predicate, bool) and predicate) or (callable(predicate) and predicate()):
        if verbose:
            err_func(msg)
        sys.exit(1)


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


def enforce_local_correct_version(name: str, version: Version) -> None:
    if directory_exists("./dist"):
        max_version = Version(0, 0, 0)
        for d in get_files("./dist"):
            d = _remove_suffix(_remove_prefix(d, f"{name}-"), ".tar.gz")
            v = Version.from_str(d)
            max_version = max(max_version, v)
        exit_if(
            version <= max_version,
            f"Specified version is '{version}' but (locally available) latest existing is '{max_version}'"
        )


def enforce_remote_correct_version(name: str, version: Version) -> None:
    pass
    # url = f"https://pypi.org/project/{name}/#history"
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    # }
    # response = requests.get(url, headers=headers)
    # if response.status_code != 200:
    #     return
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
