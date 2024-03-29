import sys
from typing import Optional, Literal

from danielutils import info, error

from .enforcers import exit_if
from .structures import Version
import quickpub.proxy

def prev_main():
    import re
    from danielutils import cmrt, cm, read_file, get_files, directory_exists, create_directory  # type:ignore

    NAME = "danielutils"

    VERSION_PATTERN = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    SETUP = "./setup.py"
    TOML = "./pyproject.toml"
    README = "./README.md"
    DIST = "./dist"
    REPORTS = "./reports"

    def get_latest(ver: str = '0.0.0') -> str:
        """returns the latest version currently in the DIST fuller

        Args:
            version (str, optional): the version to compare against. Defaults to '0.0.0'.

        Returns:
            str: the biggest version number
        """
        if not directory_exists(DIST):
            return ver
        DIST_PATTERN = NAME + r"-(\d+)\.(\d+)\.(\d+)\.tar\.gz"
        best = ver
        for filename in get_files(DIST):
            a1, b1, c1 = best.split(".")
            match = re.match(DIST_PATTERN, filename)
            if match:
                a2, b2, c2 = match.groups()
                other_version = f"{a2}.{b2}.{c2}"
                if int(a2) > int(a1):
                    best = other_version
                elif int(a2) == int(a1):
                    if int(b2) > int(b1):
                        best = other_version
                    elif int(b2) == int(b1):
                        if int(c2) > int(c1):
                            best = other_version
        return best

    def main(ver: str):
        """main function, create a new release and update the files and call terminal to upload the release

        Args:
            version (str): the new version
        """

        latest = get_latest(ver)
        if latest != ver:
            print(f"{ver} is not the latest version, found {latest}, cancelling...")
            exit()
        print("Creating new distribution...")
        ret, stdout, stderr = cm("python", "setup.py", "sdist")
        if ret != 0:
            print(stderr)
            exit()
        print("Created dist successfully")
        ret, stdout, stderr = cm("wt.exe",
                                 "twine", "upload", "--config-file", ".pypirc", f"dist/{NAME}-{ver}.tar.gz")

    def pytest() -> bool:
        """run pytest

        Returns:
            bool: success status
        """

        def has_fails(pytest_out: str) -> bool:
            RE = r'=+ (?:(?P<FAIL>\d+ failed), )?(?P<PASS>\d+ passed) in [\d\.]+s =+'
            if not re.match(RE, pytest_out):
                print("Failed to match pytest output")
                return True

            res = re.findall(RE, pytest_out)[0]
            failed = int(res[0].split()[0]) if res[0] != "" else 0
            return failed > 0

        COMMAND = "pytest"
        if input("Do you want to generate a report as well? <y|n>: ") == "y":
            COMMAND += " --html=pytest_report.html"
        COMMAND += f" > {REPORTS}/pytest.txt"
        print("running pytest")
        code, stdout, stderr = cm(COMMAND)
        if code != 0:
            err = stderr.decode()
            if err != "":
                print(err)
                return False
        with open(f"{REPORTS}/pytest.txt", "r", encoding="utf8") as f:
            summary = f.readlines()[-1]
        if has_fails(summary):
            print(summary)
            return False
        return True

    def pylint(config_file_path: str = "./.pylintrc") -> None:
        """run pylint
        """
        print("running pylint...")
        for i, line in cmrt("pylint", "--rcfile", config_file_path,
                            f"./{NAME}", ">", f"{REPORTS}/pylint.txt"):
            print(line.decode(), end="")

    def git(ver: str) -> None:
        """will add recent changes and automatically commit to git after the publication
        """

    def mypy(config_file_path: str = "mypy.ini") -> None:
        """run mypy
        """
        print("running mypy")
        with open(f"{REPORTS}/mypy.txt", "w", encoding="utf8") as f:
            for i, line in cmrt("mypy", "--config-file", config_file_path,
                                f"./{NAME}"):
                f.write(line.decode())
                print(line.decode(), end="")

    if __name__ == "__main__":
        if not directory_exists(REPORTS):
            create_directory(REPORTS)
        has_passed_tests = pytest()
        if True:
            print("Passed all tests!")
            pylint()
            mypy()
            version = input(
                f"Please supply a new version number (LATEST = {get_latest()}): ")
            if re.match(VERSION_PATTERN, version):
                main(version)
                git(version)
                print("DONE")
            else:
                print("invalid version. example 1.0.5.20")


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
    ret, stdout, stderr = quickpub.proxy.cm("twine", "upload", "--config-file", ".pypirc", f"dist/{name}-{version}.tar.gz")
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


def metrics(testing_client: Optional[Literal["pytest", "unitest"]] = None):
    pass


__all__ = [
    "build",
    "upload",
    "commit",
    "metrics"
]
