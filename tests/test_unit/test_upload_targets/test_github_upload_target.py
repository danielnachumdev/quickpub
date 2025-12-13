import unittest
from unittest.mock import patch, MagicMock

from quickpub import ExitEarlyError
from quickpub.strategies.implementations.upload_targets.github_upload_target import (
    GithubUploadTarget,
)

from tests.base_test_classes import BaseTestClass


class TestGithubUploadTarget(BaseTestClass):
    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.exit_if"
    )
    @patch("quickpub.strategies.implementations.upload_targets.github_upload_target.cm")
    def test_upload_success(self, mock_cm, mock_exit_if) -> None:
        mock_cm.return_value = (0, b"success", b"")
        target = GithubUploadTarget(verbose=False)
        target.upload(version="1.0.0")

        self.assertEqual(mock_cm.call_count, 3)
        mock_cm.assert_any_call("git add .")
        mock_cm.assert_any_call('git commit -m "updated to version 1.0.0"')
        mock_cm.assert_any_call("git push")
        mock_exit_if.assert_not_called()

    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.exit_if"
    )
    @patch("quickpub.strategies.implementations.upload_targets.github_upload_target.cm")
    def test_upload_failure_at_add(self, mock_cm, mock_exit_if) -> None:
        mock_cm.return_value = (1, b"", b"error message")
        target = GithubUploadTarget(verbose=False)
        target.upload(version="1.0.0")

        mock_exit_if.assert_called_once()
        args, kwargs = mock_exit_if.call_args
        self.assertTrue(args[0])
        self.assertIn("error message", args[1])

    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.exit_if"
    )
    @patch("quickpub.strategies.implementations.upload_targets.github_upload_target.cm")
    def test_upload_failure_at_commit(self, mock_cm, mock_exit_if) -> None:
        mock_cm.side_effect = [
            (0, b"success", b""),
            (1, b"", b"commit error"),
            (0, b"success", b""),
        ]
        target = GithubUploadTarget(verbose=False)
        target.upload(version="1.0.0")

        self.assertEqual(mock_cm.call_count, 2)
        mock_exit_if.assert_called_once()
        args, kwargs = mock_exit_if.call_args
        self.assertTrue(args[0])
        self.assertIn("commit error", args[1])

    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.exit_if"
    )
    @patch("quickpub.strategies.implementations.upload_targets.github_upload_target.cm")
    def test_upload_failure_at_push(self, mock_cm, mock_exit_if) -> None:
        mock_cm.side_effect = [
            (0, b"success", b""),
            (0, b"success", b""),
            (1, b"", b"push error"),
        ]
        target = GithubUploadTarget(verbose=False)
        target.upload(version="1.0.0")

        self.assertEqual(mock_cm.call_count, 3)
        mock_exit_if.assert_called_once()
        args, kwargs = mock_exit_if.call_args
        self.assertTrue(args[0])
        self.assertIn("push error", args[1])

    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.exit_if"
    )
    @patch("quickpub.strategies.implementations.upload_targets.github_upload_target.cm")
    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.logger"
    )
    def test_upload_verbose_mode(self, mock_logger, mock_cm, mock_exit_if) -> None:
        mock_cm.return_value = (0, b"success", b"")
        target = GithubUploadTarget(verbose=True)
        target.upload(version="1.0.0")

        debug_calls = [call[0][1] for call in mock_logger.debug.call_args_list]
        self.assertIn("Staging files for Git commit", debug_calls)
        self.assertIn(
            "Committing changes with message 'updated to version 1.0.0'", debug_calls
        )
        self.assertIn("Pushing changes to GitHub", debug_calls)

    @patch(
        "quickpub.strategies.implementations.upload_targets.github_upload_target.exit_if"
    )
    @patch("quickpub.strategies.implementations.upload_targets.github_upload_target.cm")
    def test_upload_with_name_parameter(self, mock_cm, mock_exit_if) -> None:
        mock_cm.return_value = (0, b"success", b"")
        target = GithubUploadTarget(verbose=False)
        target.upload(name="testpackage", version="1.0.0")

        self.assertEqual(mock_cm.call_count, 3)
        mock_cm.assert_any_call('git commit -m "updated to version 1.0.0"')


if __name__ == "__main__":
    unittest.main()
