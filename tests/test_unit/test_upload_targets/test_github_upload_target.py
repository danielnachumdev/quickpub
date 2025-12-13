import unittest
from unittest.mock import patch

from quickpub import ExitEarlyError
from quickpub.strategies.implementations.upload_targets.github_upload_target import (
    GithubUploadTarget,
)

from tests.base_test_classes import BaseTestClass


class TestGithubUploadTarget(BaseTestClass):
    @patch("quickpub.enforcers.exit_if")
    @patch("quickpub.proxy.cm")
    def test_upload_success(self, mock_cm, mock_exit_if) -> None:
        mock_cm.return_value = (0, b"success", b"")
        target = GithubUploadTarget(verbose=False)
        target.upload(name="testpackage", version="1.0.0")

        self.assertEqual(mock_cm.call_count, 3)
        mock_cm.assert_any_call("git add .")
        mock_cm.assert_any_call('git commit -m "updated to version 1.0.0"')
        mock_cm.assert_any_call("git push")
        mock_exit_if.assert_not_called()

    @patch("quickpub.proxy.cm")
    def test_upload_failure_at_add(self, mock_cm) -> None:
        mock_cm.side_effect = [
            (1, b"", b"error message"),
            (0, b"success", b""),
            (0, b"success", b""),
        ]
        target = GithubUploadTarget(verbose=False)
        with self.assertRaises(ExitEarlyError):
            target.upload(name="testpackage", version="1.0.0")

    @patch("quickpub.proxy.cm")
    def test_upload_failure_at_commit(self, mock_cm) -> None:
        mock_cm.side_effect = [
            (0, b"success", b""),
            (1, b"", b"commit error"),
            (0, b"success", b""),
        ]
        target = GithubUploadTarget(verbose=False)
        with self.assertRaises(ExitEarlyError):
            target.upload(name="testpackage", version="1.0.0")

        self.assertEqual(mock_cm.call_count, 2)

    @patch("quickpub.proxy.cm")
    def test_upload_failure_at_push(self, mock_cm) -> None:
        mock_cm.side_effect = [
            (0, b"success", b""),
            (0, b"success", b""),
            (1, b"", b"push error"),
        ]
        target = GithubUploadTarget(verbose=False)
        with self.assertRaises(ExitEarlyError):
            target.upload(name="testpackage", version="1.0.0")

        self.assertEqual(mock_cm.call_count, 3)

    @patch("quickpub.proxy.cm")
    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.logger"
    )
    def test_upload_verbose_mode(self, mock_logger, mock_cm) -> None:
        mock_cm.return_value = (0, b"success", b"")
        target = GithubUploadTarget(verbose=True)
        target.upload(name="testpackage", version="1.0.0")

        debug_calls = [str(call) for call in mock_logger.debug.call_args_list]
        debug_messages = " ".join(debug_calls)
        self.assertIn("Staging files for Git commit", debug_messages)
        self.assertIn("Committing changes with message", debug_messages)
        self.assertIn("Pushing changes to GitHub", debug_messages)

    @patch("quickpub.proxy.cm")
    def test_upload_with_name_parameter(self, mock_cm) -> None:
        mock_cm.return_value = (0, b"success", b"")
        target = GithubUploadTarget(verbose=False)
        target.upload(name="testpackage", version="1.0.0")

        self.assertEqual(mock_cm.call_count, 3)
        mock_cm.assert_any_call('git commit -m "updated to version 1.0.0"')


if __name__ == "__main__":
    unittest.main()
