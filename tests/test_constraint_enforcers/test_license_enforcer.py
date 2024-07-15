import unittest

from danielutils import create_file, delete_file

from quickpub import LicenseEnforcer
from utils import AutoCWDTestCase

TMP_LICENSE_PATH: str = "./TMP_LICENSE"


class TestLicenseEnforcer(AutoCWDTestCase):
    def test_license_exists_should_not_fail(self) -> None:
        exp = None
        create_file(TMP_LICENSE_PATH)
        LicenseEnforcer(TMP_LICENSE_PATH).enforce()

    def test_license_doesnt_exists_should_fail(self) -> None:
        with self.assertRaises(LicenseEnforcer.EXCEPTION_TYPE):
            LicenseEnforcer(TMP_LICENSE_PATH).enforce()
