from quickpub import LocalVersionEnforcer, Version

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory

PACKAGE_NAME: str = "foo"
LOWEST_VERSION: Version = Version.from_str("0.0.0")
HIGHER_VERSION: Version = Version.from_str("1.0.0")


class TestLocalVersionEnforcer(BaseTestClass):
    def test_no_dist_folder_should_pass(self) -> None:
        with temporary_test_directory() as tmp_dir:
            LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=LOWEST_VERSION)

    def test_empty_dist_folder_should_pass(self) -> None:
        with temporary_test_directory() as tmp_dir:
            dist_dir = tmp_dir / "dist"
            dist_dir.mkdir()
            LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=LOWEST_VERSION)

    def test_should_pass(self) -> None:
        with temporary_test_directory() as tmp_dir:
            dist_dir = tmp_dir / "dist"
            dist_dir.mkdir()
            (dist_dir / f"{PACKAGE_NAME}-{LOWEST_VERSION}").touch()
            LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=HIGHER_VERSION)

    def test_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            dist_dir = tmp_dir / "dist"
            dist_dir.mkdir()
            (dist_dir / f"{PACKAGE_NAME}-{LOWEST_VERSION}.tar.gz").touch()
            with self.assertRaises(LocalVersionEnforcer.EXCEPTION_TYPE):
                LocalVersionEnforcer().enforce(
                    name=PACKAGE_NAME, version=LOWEST_VERSION
                )
