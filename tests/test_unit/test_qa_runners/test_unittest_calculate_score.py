import unittest
from unittest.mock import patch, MagicMock
import re

from quickpub.strategies.implementations.quality_assurance_runners.unittest_qa_runner import UnittestRunner
from quickpub.enforcers import ExitEarlyError


class TestUnittestCalculateScore(unittest.TestCase):
    """Test cases for UnittestRunner._calculate_score method."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = UnittestRunner(target="./tests", bound=">=0.8", no_tests_score=0.5)

    def test_perfect_score_all_tests_pass(self):
        """Test perfect score when all tests pass."""
        lines = [
            "test_module.py",
            ".",
            "Ran 5 tests in 0.001s",
            "",
            "OK"
        ]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_perfect_score_with_skipped_tests(self):
        """Test perfect score when all tests pass but some are skipped."""
        lines = [
            "test_module.py",
            ".",
            "Ran 5 tests in 0.001s",
            "",
            "OK (skipped=2)"
        ]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_score_with_failures_only(self):
        """Test score calculation with failures only."""
        lines = [
            "test_module.py",
            "FF",
            "Ran 5 tests in 0.001s",
            "",
            "FAILED (failures=2)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (2 / 5)  # 1 - (2/5) = 0.6
        self.assertEqual(score, expected_score)

    def test_score_with_errors_only(self):
        """Test score calculation with errors only."""
        lines = [
            "test_module.py",
            "EE",
            "Ran 5 tests in 0.001s",
            "",
            "FAILED (errors=2)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (2 / 5)  # 1 - (2/5) = 0.6
        self.assertEqual(score, expected_score)

    def test_score_with_both_failures_and_errors(self):
        """Test score calculation with both failures and errors."""
        lines = [
            "test_module.py",
            "FFE",
            "Ran 5 tests in 0.001s",
            "",
            "FAILED (failures=2, errors=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (2 + 1) / 5  # 1 - (3/5) = 0.4
        self.assertEqual(score, expected_score)

    def test_score_with_failures_errors_and_skipped(self):
        """Test score calculation with failures, errors, and skipped tests."""
        lines = [
            "test_module.py",
            "FFE",
            "Ran 5 tests in 0.001s",
            "",
            "FAILED (failures=2, errors=1, skipped=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (2 + 1) / 5  # 1 - (3/5) = 0.4
        self.assertEqual(score, expected_score)

    def test_score_with_partial_failures(self):
        """Test score calculation with partial failures."""
        lines = [
            "test_module.py",
            "F..",
            "Ran 3 tests in 0.001s",
            "",
            "FAILED (failures=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (1 / 3)  # 1 - (1/3) = 0.666...
        self.assertAlmostEqual(score, expected_score, places=6)

    def test_zero_tests_returns_no_tests_score(self):
        """Test that zero tests returns the no_tests_score."""
        lines = [
            "test_module.py",
            "",
            "Ran 0 tests in 0.001s",
            "",
            "OK"
        ]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, self.runner.no_tests_score)

    def test_zero_tests_with_custom_no_tests_score(self):
        """Test zero tests with custom no_tests_score."""
        runner = UnittestRunner(target="./tests", bound=">=0.8", no_tests_score=0.8)
        lines = [
            "test_module.py",
            "",
            "Ran 0 tests in 0.001s",
            "",
            "OK"
        ]
        score = runner._calculate_score(0, lines)
        self.assertEqual(score, 0.8)

    def test_single_test_passes(self):
        """Test score calculation with single passing test."""
        lines = [
            "test_module.py",
            ".",
            "Ran 1 test in 0.001s",
            "",
            "OK"
        ]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_single_test_fails(self):
        """Test score calculation with single failing test."""
        lines = [
            "test_module.py",
            "F",
            "Ran 1 test in 0.001s",
            "",
            "FAILED (failures=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 0.0)

    def test_single_test_error(self):
        """Test score calculation with single test error."""
        lines = [
            "test_module.py",
            "E",
            "Ran 1 test in 0.001s",
            "",
            "FAILED (errors=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 0.0)

    def test_all_tests_fail(self):
        """Test score calculation when all tests fail."""
        lines = [
            "test_module.py",
            "FFF",
            "Ran 3 tests in 0.001s",
            "",
            "FAILED (failures=3)"
        ]
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 0.0)

    def test_all_tests_error(self):
        """Test score calculation when all tests error."""
        lines = [
            "test_module.py",
            "EEE",
            "Ran 3 tests in 0.001s",
            "",
            "FAILED (errors=3)"
        ]
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 0.0)

    def test_mixed_failures_and_errors_all_fail(self):
        """Test score calculation when all tests fail with mixed failures and errors."""
        lines = [
            "test_module.py",
            "FFE",
            "Ran 3 tests in 0.001s",
            "",
            "FAILED (failures=2, errors=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 0.0)

    def test_verbose_parameter_ignored(self):
        """Test that verbose parameter doesn't affect score calculation."""
        lines = [
            "test_module.py",
            "F",
            "Ran 1 test in 0.001s",
            "",
            "FAILED (failures=1)"
        ]
        score_verbose = self.runner._calculate_score(1, lines, verbose=True)
        score_normal = self.runner._calculate_score(1, lines, verbose=False)
        self.assertEqual(score_verbose, score_normal)

    def test_ok_with_skipped_tests_different_formats(self):
        """Test OK with various skipped test formats."""
        test_cases = [
            "OK (skipped=1)",
            "OK (skipped=5)",
            "OK (skipped=0)",
        ]
        
        for ok_line in test_cases:
            with self.subTest(ok_line=ok_line):
                lines = [
                    "test_module.py",
                    ".",
                    "Ran 1 test in 0.001s",
                    "",
                    ok_line
                ]
                score = self.runner._calculate_score(0, lines)
                self.assertEqual(score, 1.0)

    def test_failed_line_various_formats(self):
        """Test various FAILED line formats."""
        test_cases = [
            ("FAILED (failures=1)", 1, 0),
            ("FAILED (errors=1)", 0, 1),
            ("FAILED (failures=2, errors=1)", 2, 1),
            ("FAILED (errors=1, failures=2)", 2, 1),
            ("FAILED (failures=1, errors=1, skipped=1)", 1, 1),
            ("FAILED (skipped=1, failures=1, errors=1)", 1, 1),
        ]
        
        for failed_line, expected_failures, expected_errors in test_cases:
            with self.subTest(failed_line=failed_line):
                lines = [
                    "test_module.py",
                    "F" * (expected_failures + expected_errors),
                    "Ran 3 tests in 0.001s",
                    "",
                    failed_line
                ]
                score = self.runner._calculate_score(1, lines)
                expected_score = 1 - (expected_failures + expected_errors) / 3
                self.assertEqual(score, expected_score)

    def test_malformed_num_tests_line_raises_exception(self):
        """Test that malformed num_tests line raises ExitEarlyError."""
        lines = [
            "test_module.py",
            ".",
            "Invalid tests line",
            "",
            "OK"
        ]
        
        with self.assertRaises(ExitEarlyError) as context:
            self.runner._calculate_score(0, lines)
        
        self.assertIn("Failed running Unittest", str(context.exception))
        self.assertIn("exit code 0", str(context.exception))

    def test_malformed_failed_line_returns_perfect_score(self):
        """Test that malformed failed line is treated as OK and returns perfect score."""
        lines = [
            "test_module.py",
            "F",
            "Ran 1 test in 0.001s",
            "",
            "INVALID_FAILED_LINE"
        ]
        
        # The function treats non-matching FAILED lines as if they were OK
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 1.0)

    def test_non_numeric_failure_count_raises_exception(self):
        """Test that non-numeric failure count raises ExitEarlyError."""
        # This would require modifying the regex pattern to match non-numeric values
        # which shouldn't happen in practice, but we test the exception handling
        lines = [
            "test_module.py",
            "F",
            "Ran 1 test in 0.001s",
            "",
            "FAILED (failures=abc)"
        ]
        
        with self.assertRaises(ExitEarlyError) as context:
            self.runner._calculate_score(1, lines)
        
        self.assertIn("Failed running Unittest", str(context.exception))

    def test_insufficient_lines_raises_exception(self):
        """Test that insufficient lines raises IndexError which becomes ExitEarlyError."""
        lines = ["Only one line"]
        
        with self.assertRaises(ExitEarlyError) as context:
            self.runner._calculate_score(0, lines)
        
        self.assertIn("Failed running Unittest", str(context.exception))

    def test_empty_lines_raises_exception(self):
        """Test that empty lines list raises IndexError which becomes ExitEarlyError."""
        lines = []
        
        with self.assertRaises(ExitEarlyError) as context:
            self.runner._calculate_score(0, lines)
        
        self.assertIn("Failed running Unittest", str(context.exception))

    def test_regex_pattern_matching_edge_cases(self):
        """Test regex pattern matching with edge cases."""
        # Test with different time formats
        test_cases = [
            "Ran 1 test in 0.001s",
            "Ran 5 tests in 1.234s", 
            "Ran 10 tests in 0.000s",
            "Ran 100 tests in 12.345s",
        ]
        
        for test_line in test_cases:
            with self.subTest(test_line=test_line):
                lines = [
                    "test_module.py",
                    ".",
                    test_line,
                    "",
                    "OK"
                ]
                score = self.runner._calculate_score(0, lines)
                self.assertEqual(score, 1.0)

    def test_failure_pattern_edge_cases(self):
        """Test failure pattern matching with edge cases."""
        test_cases = [
            ("FAILED (failures=0)", 0, 0),
            ("FAILED (errors=0)", 0, 0),
            ("FAILED (failures=0, errors=0)", 0, 0),
            ("FAILED (failures=1, errors=0)", 1, 0),
            ("FAILED (failures=0, errors=1)", 0, 1),
        ]
        
        for failed_line, expected_failures, expected_errors in test_cases:
            with self.subTest(failed_line=failed_line):
                lines = [
                    "test_module.py",
                    "F" * (expected_failures + expected_errors),
                    "Ran 2 tests in 0.001s",
                    "",
                    failed_line
                ]
                score = self.runner._calculate_score(1, lines)
                expected_score = 1 - (expected_failures + expected_errors) / 2
                self.assertEqual(score, expected_score)

    def test_score_precision(self):
        """Test score calculation precision with various ratios."""
        # Test case that should result in repeating decimal
        lines = [
            "test_module.py",
            "F",
            "Ran 3 tests in 0.001s",
            "",
            "FAILED (failures=1)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (1 / 3)  # 0.666...
        self.assertAlmostEqual(score, expected_score, places=6)

    def test_large_number_of_tests(self):
        """Test score calculation with large number of tests."""
        lines = [
            "test_module.py",
            "F" * 100,  # 100 failures
            "Ran 1000 tests in 0.001s",
            "",
            "FAILED (failures=100)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (100 / 1000)  # 0.9
        self.assertEqual(score, expected_score)

    def test_very_small_score(self):
        """Test score calculation resulting in very small score."""
        lines = [
            "test_module.py",
            "F" * 99,  # 99 failures
            "Ran 100 tests in 0.001s",
            "",
            "FAILED (failures=99)"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 1 - (99 / 100)  # 0.01
        self.assertEqual(score, expected_score)

    @patch('quickpub.strategies.implementations.quality_assurance_runners.unittest_qa_runner.logger')
    def test_logging_calls(self, mock_logger):
        """Test that appropriate logging calls are made."""
        lines = [
            "test_module.py",
            "F",
            "Ran 1 test in 0.001s",
            "",
            "FAILED (failures=1)"
        ]
        
        self.runner._calculate_score(1, lines)
        
        # Check that info logging was called
        self.assertTrue(mock_logger.info.called)
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertIn("Calculating unittest score from test results", info_calls)
        self.assertIn("Unittest score calculated: %.3f (tests: %d, failed: %d, errors: %d)", info_calls)

    @patch('quickpub.strategies.implementations.quality_assurance_runners.unittest_qa_runner.logger')
    def test_logging_no_tests(self, mock_logger):
        """Test logging when no tests are found."""
        lines = [
            "test_module.py",
            "",
            "Ran 0 tests in 0.001s",
            "",
            "OK"
        ]
        
        self.runner._calculate_score(0, lines)
        
        # Check that no_tests_score logging was called
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        self.assertIn("No tests found, returning no_tests_score: %s", info_calls)

    @patch('quickpub.strategies.implementations.quality_assurance_runners.unittest_qa_runner.logger')
    def test_logging_exception(self, mock_logger):
        """Test logging when exception occurs."""
        lines = ["Only one line"]  # This will cause an IndexError
        
        with self.assertRaises(ExitEarlyError):
            self.runner._calculate_score(0, lines)
        
        # Check that error logging was called
        self.assertTrue(mock_logger.error.called)
        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        self.assertIn("Failed to calculate unittest score", error_calls[0])


if __name__ == '__main__':
    unittest.main()
