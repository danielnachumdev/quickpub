import unittest
from typing import List

from quickpub.strategies.implementations.quality_assurance_runners.pytest_qa_runner import (
    PytestRunner,
)
from quickpub.enforcers import ExitEarlyError


class TestPytestCalculateScore(unittest.TestCase):
    """Test cases for PytestRunner._calculate_score method."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.runner = PytestRunner(
            target="./tests", bound=">=0.8", no_tests_score=0.5, no_output_score=0.0
        )

    def test_perfect_score_all_tests_pass(self) -> None:
        """Test perfect score when all tests pass."""
        lines = ["============ 5 passed in 2.1s ============"]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_score_with_failures(self) -> None:
        """Test score calculation with failures."""
        lines = ["============ 2 failed, 10 passed in 5.23s ============"]
        score = self.runner._calculate_score(1, lines)
        expected_score = 10 / (10 + 2 + 0)
        self.assertEqual(score, expected_score)

    def test_score_with_failures_first(self) -> None:
        """Test score when failed comes before passed."""
        lines = ["============ 3 failed, 7 passed in 3.5s ============"]
        score = self.runner._calculate_score(1, lines)
        expected_score = 7 / (7 + 3 + 0)
        self.assertEqual(score, expected_score)

    def test_score_with_passed_first(self) -> None:
        """Test score when passed comes before failed."""
        lines = ["============ 10 passed, 2 failed in 5.23s ============"]
        score = self.runner._calculate_score(1, lines)
        expected_score = 10 / (10 + 2 + 0)
        self.assertEqual(score, expected_score)

    def test_score_with_skipped_tests(self) -> None:
        """Test score calculation with skipped tests."""
        lines = ["============ 247 passed, 3 skipped in 116.62s ============"]
        score = self.runner._calculate_score(0, lines)
        expected_score = 247 / (247 + 0 + 3)
        self.assertEqual(score, expected_score)

    def test_score_with_skipped_reduces_score(self) -> None:
        """Test that skipped tests reduce the score (not counted as passed)."""
        lines = ["============ 10 passed, 5 skipped in 2.1s ============"]
        score = self.runner._calculate_score(0, lines)
        expected_score = 10 / (10 + 0 + 5)
        self.assertEqual(score, expected_score)
        self.assertLess(score, 1.0)

    def test_score_with_warnings(self) -> None:
        """Test score calculation with warnings."""
        lines = ["============ 100 passed, 1 warning in 10.5s ============"]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_score_with_skipped_and_warnings(self) -> None:
        """Test score calculation with skipped tests and warnings."""
        lines = [
            "============ 247 passed, 3 skipped, 1 warning in 116.62s (0:01:56) ============"
        ]
        score = self.runner._calculate_score(0, lines)
        expected_score = 247 / (247 + 0 + 3)
        self.assertEqual(score, expected_score)

    def test_score_with_time_in_parentheses(self) -> None:
        """Test score calculation with time format in parentheses."""
        lines = ["============ 50 passed in 5.5s (0:00:05) ============"]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_score_with_all_components(self) -> None:
        """Test score calculation with all components: failed, passed, skipped, warnings, and time."""
        lines = [
            "============ 2 failed, 245 passed, 3 skipped, 1 warning in 116.62s (0:01:56) ============"
        ]
        score = self.runner._calculate_score(1, lines)
        expected_score = 245 / (245 + 2 + 3)
        self.assertEqual(score, expected_score)

    def test_score_with_only_failed(self) -> None:
        """Test score calculation with only failed tests."""
        lines = ["============ 5 failed in 2.1s ============"]
        score = self.runner._calculate_score(1, lines)
        self.assertEqual(score, 0.0)

    def test_no_tests_ran(self) -> None:
        """Test score when no tests ran."""
        lines = ["no tests ran"]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 0.5)

    def test_no_tests_ran_case_insensitive(self) -> None:
        """Test score when no tests ran (case insensitive)."""
        lines = ["NO TESTS RAN"]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 0.5)

    def test_no_output_returns_no_output_score(self) -> None:
        """Test score when there is no output."""
        lines: List[str] = []
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 0.0)

    def test_no_passed_or_failed_returns_no_tests_score(self) -> None:
        """Test score when output has no passed or failed counts."""
        lines = ["============ in 2.1s ============"]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 0.5)

    def test_malformed_output_raises_exception(self) -> None:
        """Test that malformed output raises ExitEarlyError."""
        lines = ["This is not a valid pytest output line"]
        with self.assertRaises(ExitEarlyError) as context:
            self.runner._calculate_score(0, lines)
        self.assertIn("Can't calculate score for pytest", str(context.exception))

    def test_finds_summary_line_from_multiple_lines(self) -> None:
        """Test that the method finds the summary line from multiple lines of output."""
        lines = [
            "test_file.py::test_function PASSED",
            "test_file.py::test_function2 PASSED",
            "============ 2 passed in 1.5s ============",
            "Some other output line",
        ]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)

    def test_finds_summary_line_with_warnings_after(self) -> None:
        """Test that the method finds summary line even when warnings appear after."""
        lines = [
            "============ 10 passed in 5.0s ============",
            "warnings summary",
            "some warning message",
        ]
        score = self.runner._calculate_score(0, lines)
        self.assertEqual(score, 1.0)
