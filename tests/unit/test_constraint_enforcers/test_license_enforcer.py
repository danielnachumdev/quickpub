from quickpub import LicenseEnforcer

from tests.base_test_classes import BaseTestClass
from tests.test_helpers import temporary_test_directory

TMP_LICENSE_PATH: str = "TMP_LICENSE"


class TestLicenseEnforcer(BaseTestClass):
    def test_license_exists_should_not_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            license_path = tmp_dir / TMP_LICENSE_PATH
            license_path.touch()
            LicenseEnforcer(str(license_path)).enforce()

    def test_license_doesnt_exists_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            license_path = tmp_dir / TMP_LICENSE_PATH
            with self.assertRaises(LicenseEnforcer.EXCEPTION_TYPE):
                LicenseEnforcer(str(license_path)).enforce()
