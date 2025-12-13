import unittest
from unittest.mock import patch, MagicMock
import os

import requests

from quickpub.proxy import cm, os_system, get

from tests.base_test_classes import BaseTestClass


class TestCm(BaseTestClass):
    @patch("quickpub.proxy.danielutils.cm")
    def test_cm_passthrough(self, mock_danielutils_cm) -> None:
        mock_danielutils_cm.return_value = (0, b"stdout", b"stderr")
        result = cm("python", "--version")
        self.assertEqual(result, (0, b"stdout", b"stderr"))
        mock_danielutils_cm.assert_called_once_with("python", "--version")

    @patch("quickpub.proxy.danielutils.cm")
    def test_cm_with_multiple_args(self, mock_danielutils_cm) -> None:
        mock_danielutils_cm.return_value = (1, b"error", b"stderr")
        result = cm("git", "add", "file.txt")
        self.assertEqual(result, (1, b"error", b"stderr"))
        mock_danielutils_cm.assert_called_once_with("git", "add", "file.txt")

    @patch("quickpub.proxy.danielutils.cm")
    def test_cm_with_kwargs(self, mock_danielutils_cm) -> None:
        mock_danielutils_cm.return_value = (0, b"output", b"")
        result = cm("command", arg1="value1", arg2="value2")
        self.assertEqual(result, (0, b"output", b""))
        mock_danielutils_cm.assert_called_once_with(
            "command", arg1="value1", arg2="value2"
        )

    @patch("quickpub.proxy.logger")
    @patch("quickpub.proxy.danielutils.cm")
    def test_cm_logging(self, mock_danielutils_cm, mock_logger) -> None:
        mock_danielutils_cm.return_value = (0, b"stdout", b"stderr")
        cm("test", "command")
        mock_logger.debug.assert_any_call("Executing command: %s", "test command")
        mock_logger.debug.assert_any_call("Command completed with return code: %d", 0)


class TestOsSystem(BaseTestClass):
    @patch("os.system")
    def test_os_system_passthrough(self, mock_os_system) -> None:
        mock_os_system.return_value = 0
        result = os_system("echo hello")
        self.assertEqual(result, 0)
        mock_os_system.assert_called_once_with("echo hello")

    @patch("os.system")
    def test_os_system_nonzero_return(self, mock_os_system) -> None:
        mock_os_system.return_value = 1
        result = os_system("false")
        self.assertEqual(result, 1)
        mock_os_system.assert_called_once_with("false")

    @patch("quickpub.proxy.logger")
    @patch("os.system")
    def test_os_system_logging(self, mock_os_system, mock_logger) -> None:
        mock_os_system.return_value = 0
        os_system("test command")
        mock_logger.debug.assert_any_call(
            "Executing system command: %s", "test command"
        )
        mock_logger.debug.assert_any_call(
            "System command completed with return code: %d", 0
        )


class TestGet(BaseTestClass):
    @patch("requests.get")
    def test_get_passthrough(self, mock_requests_get) -> None:
        mock_response = MagicMock(spec=requests.models.Response)
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        result = get("https://example.com")
        self.assertEqual(result, mock_response)
        mock_requests_get.assert_called_once_with("https://example.com")

    @patch("requests.get")
    def test_get_with_kwargs(self, mock_requests_get) -> None:
        mock_response = MagicMock(spec=requests.models.Response)
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        result = get("https://example.com", timeout=5, headers={"User-Agent": "test"})
        self.assertEqual(result, mock_response)
        mock_requests_get.assert_called_once_with(
            "https://example.com", timeout=5, headers={"User-Agent": "test"}
        )

    @patch("requests.get")
    def test_get_different_status_codes(self, mock_requests_get) -> None:
        for status_code in [200, 404, 500]:
            mock_response = MagicMock(spec=requests.models.Response)
            mock_response.status_code = status_code
            mock_requests_get.return_value = mock_response

            result = get("https://example.com")
            self.assertEqual(result.status_code, status_code)

    @patch("quickpub.proxy.logger")
    @patch("requests.get")
    def test_get_logging(self, mock_requests_get, mock_logger) -> None:
        mock_response = MagicMock(spec=requests.models.Response)
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        get("https://example.com")
        mock_logger.debug.assert_any_call(
            "Making HTTP GET request to: %s", "https://example.com"
        )
        mock_logger.debug.assert_any_call(
            "HTTP GET request completed with status code: %d", 200
        )

    @patch("quickpub.proxy.logger")
    @patch("requests.get")
    def test_get_logging_no_url(self, mock_requests_get, mock_logger) -> None:
        mock_response = MagicMock(spec=requests.models.Response)
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        get()
        mock_logger.debug.assert_any_call(
            "Making HTTP GET request to: %s", "URL not provided"
        )


if __name__ == "__main__":
    unittest.main()
