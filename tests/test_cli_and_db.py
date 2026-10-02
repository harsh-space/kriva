import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from router import cli
from router.db import log_run, recent_runs
from router.providers.base import Result


class CliTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.repo_info = {
            "root": str(Path.cwd()),
            "commit_sha": "abc123",
            "diff": "diff --git a/file.py b/file.py",
        }

    def test_ask_prints_response_and_logs_success(self):
        class FakeProvider:
            name = "fake"
            model = "fake-model"

            async def generate(provider_self, prompt, context):
                self.assertEqual(prompt, "explain this")
                self.assertIn(self.repo_info["diff"], context)
                return Result(
                    "explained",
                    provider_self.name,
                    provider_self.model,
                    4,
                    6,
                    9,
                )

        with patch.object(cli, "read_repo", return_value=self.repo_info), patch.dict(
            cli.PROVIDERS, {"fake": FakeProvider}
        ), patch.object(cli, "log_run") as log:
            result = self.runner.invoke(
                cli.app, ["ask", "explain this", "--provider", "fake"]
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("explained", result.output)
        fields = log.call_args.kwargs
        self.assertEqual(fields["success"], 1)
        self.assertEqual(fields["output"], "explained")
        self.assertEqual(fields["tokens_in"], 4)
        self.assertEqual(fields["tokens_out"], 6)
        self.assertIsNone(fields["error"])

    def test_ask_logs_provider_failure_and_returns_nonzero(self):
        class FailingProvider:
            name = "fake"
            model = "fake-model"

            async def generate(self, prompt, context):
                raise RuntimeError("provider unavailable")

        with patch.object(cli, "read_repo", return_value=self.repo_info), patch.dict(
            cli.PROVIDERS, {"fake": FailingProvider}
        ), patch.object(cli, "log_run") as log:
            result = self.runner.invoke(
                cli.app, ["ask", "explain this", "--provider", "fake"]
            )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("provider unavailable", result.output)
        fields = log.call_args.kwargs
        self.assertEqual(fields["success"], 0)
        self.assertEqual(fields["error"], "RuntimeError: provider unavailable")

    def test_unknown_provider_is_rejected(self):
        result = self.runner.invoke(
            cli.app, ["ask", "task", "--provider", "does-not-exist"]
        )
        self.assertEqual(result.exit_code, 2)
        self.assertIn("Unknown provider", result.output)

    def test_not_a_git_repo_is_reported(self):
        with patch.object(
            cli, "read_repo", side_effect=cli.NotAGitRepo("not a repository")
        ), patch.object(cli, "log_run") as log:
            result = self.runner.invoke(cli.app, ["ask", "task"])

        self.assertEqual(result.exit_code, 2)
        self.assertIn("not a repository", result.output)
        log.assert_not_called()


class DatabaseTests(unittest.TestCase):
    def test_run_fields_are_persisted_and_returned(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "nested" / "runs.db"
            with patch.dict(os.environ, {"ROUTER_DB": str(database)}):
                log_run(
                    repo="repo",
                    commit_sha="abc123",
                    provider="nvidia",
                    model="nvidia/nemotron-3-ultra-550b-a55b",
                    prompt="task",
                    output="answer",
                    tokens_in=12,
                    tokens_out=7,
                    latency_ms=42,
                    success=1,
                    error=None,
                )
                rows = recent_runs()

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0][2:6],
            (
                "nvidia",
                "nvidia/nemotron-3-ultra-550b-a55b",
                12,
                7,
            ),
        )
        self.assertEqual(rows[0][6:], (42, 1))


if __name__ == "__main__":
    unittest.main()
