from quickpub import ExitEarlyError, Version
from quickpub.dist_files import find_sdist, normalize_dist_name

from tests.common.base_test_classes import BaseTestClass
from tests.common.helpers import temporary_test_directory


class TestNormalizeDistName(BaseTestClass):
    def test_underscores_become_hyphens(self) -> None:
        self.assertEqual(normalize_dist_name("gp_wrapper"), "gp-wrapper")

    def test_mixed_separators(self) -> None:
        self.assertEqual(normalize_dist_name("My.Package_Name"), "my-package-name")


class TestFindSdist(BaseTestClass):
    def test_finds_raw_name(self) -> None:
        with temporary_test_directory() as tmp_dir:
            dist_dir = tmp_dir / "dist"
            dist_dir.mkdir()
            sdist = dist_dir / "testpackage-1.0.0.tar.gz"
            sdist.write_bytes(b"dummy")

            found = find_sdist(dist_dir, "testpackage", "1.0.0")
            self.assertEqual(found, sdist)

    def test_finds_normalized_name(self) -> None:
        with temporary_test_directory() as tmp_dir:
            dist_dir = tmp_dir / "dist"
            dist_dir.mkdir()
            sdist = dist_dir / "gp-wrapper-1.0.0.tar.gz"
            sdist.write_bytes(b"dummy")

            found = find_sdist(dist_dir, "gp_wrapper", Version(1, 0, 0))
            self.assertEqual(found, sdist)

    def test_missing_sdist_raises(self) -> None:
        with temporary_test_directory() as tmp_dir:
            dist_dir = tmp_dir / "dist"
            dist_dir.mkdir()
            with self.assertRaises(ExitEarlyError):
                find_sdist(dist_dir, "testpackage", "1.0.0")
