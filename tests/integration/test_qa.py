import os
import unittest

from quickpub import CondaPythonProvider, ExitEarlyError
from quickpub.qa import qa

from tests.common.base_test_classes import AsyncBaseTestClass
from tests.common.helpers import conda_base_env_available, conda_is_available, temporary_test_directory

PACKAGE_NAME: str = "foo"


class TestCondaPythonProvider(AsyncBaseTestClass):
    @unittest.skipUnless(conda_base_env_available(), "conda base env required")
    async def test_simplest_case_should_succeed(self) -> None:
        with temporary_test_directory() as tmp_dir:
            package_dir = tmp_dir / PACKAGE_NAME
            package_dir.mkdir()
            (package_dir / "__init__.py").touch()
            await qa(
                python_provider=CondaPythonProvider(["base"]),
                quality_assurance_strategies=[],
                package_name=PACKAGE_NAME,
                src_folder_path=str(package_dir),
                dependencies=[],
            )

    @unittest.skipUnless(conda_base_env_available(), "conda base env required")
    async def test_wrong_src_folder_path_should_fail(self) -> None:
        with temporary_test_directory() as tmp_dir:
            await qa(
                python_provider=CondaPythonProvider(["base"]),
                quality_assurance_strategies=[],
                package_name=PACKAGE_NAME,
                src_folder_path=str(tmp_dir / "akjsbgfakjgbakls"),
                dependencies=[],
            )

    @unittest.skipUnless(conda_is_available(), "conda required")
    async def test_non_existing_env_should_skip(self) -> None:
        NON_EXISTENT_ENV_NAME: str = "sdjbnglksjdgnwkerjg"
        with self.assertRaises(ExitEarlyError):
            async for x in CondaPythonProvider([NON_EXISTENT_ENV_NAME]):
                pass
