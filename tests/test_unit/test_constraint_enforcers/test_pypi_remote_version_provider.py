import unittest
from typing import Optional
from unittest.mock import patch, MagicMock, Mock

from requests import Response

from quickpub import PypiRemoteVersionEnforcer, Version, ExitEarlyError

PACKAGE_NAME: str = "foo"
LOWEST_VERSION: Version = Version.from_str("0.0.0")
HIGHER_VERSION: Version = Version.from_str("1.0.0")


def create_response(
        include_content: bool = False,
        status_code: int = 200,
        target_package_name: str = PACKAGE_NAME,
        target_package_version: Version = LOWEST_VERSION
) -> Response:
    response = Mock(status_code=status_code)

    if include_content:
        # Create HTML in the format of PyPI simple package index
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta name="pypi:repository-version" content="1.3">
  <title>Links for {target_package_name}</title>
</head>
<body>
<h1>Links for {target_package_name}</h1>
<a href="https://files.pythonhosted.org/packages/test/test123/{target_package_name}-{target_package_version}.tar.gz#sha256=test123" data-requires-python="&gt;=3.8.0" >{target_package_name}-{target_package_version}.tar.gz</a><br />
<a href="https://files.pythonhosted.org/packages/test/test456/{target_package_name}-0.5.0.tar.gz#sha256=test456" data-requires-python="&gt;=3.8.0" >{target_package_name}-0.5.0.tar.gz</a><br />
<a href="https://files.pythonhosted.org/packages/test/test789/{target_package_name}-0.4.0.tar.gz#sha256=test789" data-requires-python="&gt;=3.8.0" >{target_package_name}-0.4.0.tar.gz</a><br />
</body>
</html>"""
        response.configure_mock(content=html_content.encode())

    return response


class TestPypiRemoteVersionProvider(unittest.TestCase):
    @patch("quickpub.strategies.implementations.constraint_enforcers.pypi_remote_version_enforcer.get",
           return_value=None)
    def test_request_failed(self, *args):
        with self.assertRaises(ExitEarlyError) as e:
            PypiRemoteVersionEnforcer().enforce(PACKAGE_NAME, HIGHER_VERSION)
        self.assertEqual(str(e.exception),
                         PypiRemoteVersionEnforcer._HTTP_FAILED_MESSAGE)

    @patch("quickpub.strategies.implementations.constraint_enforcers.pypi_remote_version_enforcer.get",
           return_value=create_response(include_content=True, target_package_version=HIGHER_VERSION))
    def test_should_fail(self, *args):
        with self.assertRaises(ExitEarlyError) as e:
            PypiRemoteVersionEnforcer().enforce(PACKAGE_NAME, LOWEST_VERSION)

    @patch("quickpub.strategies.implementations.constraint_enforcers.pypi_remote_version_enforcer.get",
           return_value=create_response(include_content=True, target_package_version=LOWEST_VERSION))
    def test_should_pass(self, *args):
        PypiRemoteVersionEnforcer().enforce(PACKAGE_NAME, HIGHER_VERSION)
