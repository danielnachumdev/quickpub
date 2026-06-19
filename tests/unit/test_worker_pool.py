import logging
import unittest
from unittest.mock import patch

from quickpub.worker_pool import WorkerPool

from tests.base_test_classes import BaseTestClass


class TestWorkerPool(BaseTestClass):
    @patch("quickpub.worker_pool.logger")
    def test_log_delegates_to_logger(self, mock_logger) -> None:
        WorkerPool.log(logging.INFO, "Test message", arg1="value1")
        mock_logger.log.assert_called_once_with(
            logging.INFO, "Test message", arg1="value1"
        )

    @patch("quickpub.worker_pool.logger")
    def test_log_with_different_levels(self, mock_logger) -> None:
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            WorkerPool.log(level, f"Message at level {level}")
            mock_logger.log.assert_called_with(level, f"Message at level {level}")

    @patch("quickpub.worker_pool.logger")
    def test_log_with_args_and_kwargs(self, mock_logger) -> None:
        WorkerPool.log(
            logging.INFO,
            "Message %s %s",
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
        )
        mock_logger.log.assert_called_once_with(
            logging.INFO,
            "Message %s %s",
            "arg1",
            "arg2",
            kwarg1="value1",
            kwarg2="value2",
        )


if __name__ == "__main__":
    unittest.main()
