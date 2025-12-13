import logging
import sys
import unittest
from unittest.mock import patch, MagicMock

from quickpub.logging_ import (
    setup_logging,
    set_log_level,
    QuickpubLogFilter,
    TqdmLoggingHandler,
)

from tests.base_test_classes import BaseTestClass


class TestQuickpubLogFilter(BaseTestClass):
    def test_filters_quickpub_logger(self) -> None:
        filter_obj = QuickpubLogFilter()
        record = logging.LogRecord(
            name="quickpub.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        self.assertTrue(filter_obj.filter(record))

    def test_filters_quickpub_submodule(self) -> None:
        filter_obj = QuickpubLogFilter()
        record = logging.LogRecord(
            name="quickpub.strategies.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        self.assertTrue(filter_obj.filter(record))

    def test_does_not_filter_non_quickpub_logger(self) -> None:
        filter_obj = QuickpubLogFilter()
        record = logging.LogRecord(
            name="other.module",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        self.assertFalse(filter_obj.filter(record))


class TestTqdmLoggingHandler(BaseTestClass):
    @patch("tqdm.tqdm")
    def test_emit_with_tqdm(self, mock_tqdm) -> None:
        handler = TqdmLoggingHandler()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        handler.emit(record)
        mock_tqdm.write.assert_called_once()

    @patch("builtins.print")
    def test_emit_without_tqdm_fallback(self, mock_print) -> None:
        import sys
        from types import ModuleType
        original_tqdm = sys.modules.get("tqdm")
        sys.modules["tqdm"] = None  # type: ignore[assignment]
        try:
            handler = TqdmLoggingHandler()
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None,
            )
            handler.format = MagicMock(return_value="Formatted message")  # type: ignore[method-assign]
            handler.emit(record)
            mock_print.assert_called_once_with("Formatted message", file=sys.stdout)
        finally:
            if original_tqdm is not None:
                sys.modules["tqdm"] = original_tqdm
            elif "tqdm" in sys.modules:
                del sys.modules["tqdm"]

    def test_emit_handles_exception(self) -> None:
        handler = TqdmLoggingHandler()
        handler.format = MagicMock(side_effect=Exception("Format error"))  # type: ignore[method-assign]
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        handler.handleError = MagicMock()  # type: ignore[method-assign]
        handler.emit(record)
        handler.handleError.assert_called_once_with(record)


class TestSetupLogging(BaseTestClass):
    def setUp(self) -> None:
        super().setUp()
        logging.getLogger().handlers.clear()

    @patch("tqdm.tqdm")
    def test_setup_logging_default_level(self, mock_tqdm) -> None:
        setup_logging(level=logging.INFO)
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], TqdmLoggingHandler)

    @patch("tqdm.tqdm")
    def test_setup_logging_custom_level(self, mock_tqdm) -> None:
        setup_logging(level=logging.DEBUG)
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.DEBUG)
        handler = logger.handlers[0]
        self.assertEqual(handler.level, logging.DEBUG)

    def test_setup_logging_fallback_to_stream_handler(self) -> None:
        import sys
        from types import ModuleType
        original_tqdm = sys.modules.get("tqdm")
        sys.modules["tqdm"] = None  # type: ignore[assignment]
        try:
            setup_logging()
            logger = logging.getLogger()
            self.assertEqual(len(logger.handlers), 1)
            self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        finally:
            if original_tqdm is not None:
                sys.modules["tqdm"] = original_tqdm
            elif "tqdm" in sys.modules:
                del sys.modules["tqdm"]

    @patch("tqdm.tqdm")
    def test_setup_logging_clears_existing_handlers(self, mock_tqdm) -> None:
        logger = logging.getLogger()
        existing_handler = logging.StreamHandler()
        logger.addHandler(existing_handler)
        self.assertEqual(len(logger.handlers), 1)

        setup_logging()
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], TqdmLoggingHandler)
        self.assertNotEqual(logger.handlers[0], existing_handler)

    @patch("tqdm.tqdm")
    def test_setup_logging_adds_filter(self, mock_tqdm) -> None:
        setup_logging()
        logger = logging.getLogger()
        handler = logger.handlers[0]
        self.assertEqual(len(handler.filters), 1)
        self.assertIsInstance(handler.filters[0], QuickpubLogFilter)

    @patch("tqdm.tqdm")
    def test_setup_logging_formatter(self, mock_tqdm) -> None:
        setup_logging()
        logger = logging.getLogger()
        handler = logger.handlers[0]
        self.assertIsNotNone(handler.formatter)
        format_str = handler.formatter._fmt
        self.assertIn("quickpub", format_str)


class TestSetLogLevel(BaseTestClass):
    def setUp(self) -> None:
        super().setUp()
        logging.getLogger().handlers.clear()

    @patch("tqdm.tqdm")
    def test_set_log_level_updates_global(self, mock_tqdm) -> None:
        setup_logging(level=logging.INFO)
        set_log_level(logging.DEBUG)
        logger = logging.getLogger()
        self.assertEqual(logger.level, logging.DEBUG)

    @patch("tqdm.tqdm")
    def test_set_log_level_updates_handlers(self, mock_tqdm) -> None:
        setup_logging(level=logging.INFO)
        logger = logging.getLogger()
        handler = logger.handlers[0]
        self.assertEqual(handler.level, logging.INFO)

        set_log_level(logging.WARNING)
        self.assertEqual(handler.level, logging.WARNING)

    @patch("tqdm.tqdm")
    def test_set_log_level_updates_all_handlers(self, mock_tqdm) -> None:
        setup_logging(level=logging.INFO)
        logger = logging.getLogger()
        handler2 = logging.StreamHandler()
        handler2.setLevel(logging.ERROR)
        logger.addHandler(handler2)

        set_log_level(logging.DEBUG)
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)
        self.assertEqual(logger.handlers[1].level, logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
