from danielutils import create_directory, create_file

from quickpub import LocalVersionEnforcer, Version
from utils import AutoCWDTestCase

PACKAGE_NAME: str = "foo"
LOWEST_VERSION: Version = Version.from_str("0.0.0")
HIGHER_VERSION: Version = Version.from_str("1.0.0")


class TestLocalVersionEnforcer(AutoCWDTestCase):
    def test_no_dist_folder_should_pass(self) -> None:
        LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=LOWEST_VERSION)

    def test_empty_dist_folder_should_pass(self) -> None:
        create_directory("./dist")
        LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=LOWEST_VERSION)

    def test_should_pass(self) -> None:
        create_directory("./dist")
        create_file(f"./dist/{PACKAGE_NAME}-{LOWEST_VERSION}")
        LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=HIGHER_VERSION)

    def test_should_fail(self) -> None:
        create_directory("./dist")
        create_file(f"./dist/{PACKAGE_NAME}-{LOWEST_VERSION}.tar.gz")
        with self.assertRaises(LocalVersionEnforcer.EXCEPTION_TYPE):
            LocalVersionEnforcer().enforce(name=PACKAGE_NAME, version=LOWEST_VERSION)
