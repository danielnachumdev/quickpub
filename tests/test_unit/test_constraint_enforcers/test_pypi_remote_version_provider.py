import unittest
from typing import Optional
from unittest.mock import patch, MagicMock, Mock

from danielutils import warning, get_current_working_directory
from requests import Response

from quickpub import PypiRemoteVersionEnforcer, Version, ExitEarlyError

PACKAGE_NAME: str = "foo"
LOWEST_VERSION: Version = Version.from_str("0.0.0")
HIGHER_VERSION: Version = Version.from_str("1.0.0")

MOCK_HTML: str = """<div> {package_name} {version} </div>"""


def create_response(include_content: bool = False, status_code: int = 200,
                    target_package_name: str = PACKAGE_NAME,
                    target_package_version: Version = LOWEST_VERSION) -> Response:
    response = Mock(status_code=status_code)

    if include_content:
        with open("./test_unit/test_constraint_enforcers/remote_example.html", "r",encoding="utf8") as f:
            raw_html = f.read()
        mock_html = raw_html.replace("quickpub", target_package_name)
        mock_html = mock_html.replace(f" {target_package_name} 1.0.3",
                                      f" {target_package_name} {target_package_version}")
        response.configure_mock(content=mock_html.encode())

    return response


class TestPypiRemoteVersionProvider(unittest.TestCase):
    @patch("quickpub.strategies.implementations.constraint_enforcers.pypi_remote_version_enforcer.get",
           return_value=None)
    def test_request_failed(self, *args):
        with self.assertRaises(ExitEarlyError) as e:
            PypiRemoteVersionEnforcer().enforce(PACKAGE_NAME, HIGHER_VERSION)
        self.assertEqual(str(e.exception), PypiRemoteVersionEnforcer._HTTP_FAILED_MESSAGE)

    @patch("quickpub.strategies.implementations.constraint_enforcers.pypi_remote_version_enforcer.get",
           return_value=create_response(include_content=True, target_package_version=HIGHER_VERSION))
    def test_should_fail(self, *args):
        with self.assertRaises(ExitEarlyError) as e:
            PypiRemoteVersionEnforcer().enforce(PACKAGE_NAME, LOWEST_VERSION)

    @patch("quickpub.strategies.implementations.constraint_enforcers.pypi_remote_version_enforcer.get",
           return_value=create_response(include_content=True, target_package_version=LOWEST_VERSION))
    def test_should_pass(self, *args):
        PypiRemoteVersionEnforcer().enforce(PACKAGE_NAME, HIGHER_VERSION)
