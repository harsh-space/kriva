import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from git import Repo

from router.repo import NotAGitRepo, read_repo


class ReadRepoTests(unittest.TestCase):
    def _make_repo(self, root: Path) -> Repo:
        repo = Repo.init(root)
        with repo.config_writer() as config:
            config.set_value("user", "name", "Kriva Tests")
            config.set_value("user", "email", "tests@example.invalid")
        tracked_file = root / "sample.py"
        tracked_file.write_text("value = 1\n", encoding="utf-8")
        repo.index.add(["sample.py"])
        repo.index.commit("initial commit")
        tracked_file.write_text("value = 2\n", encoding="utf-8")
        return repo

    def test_reads_repo_root_commit_and_current_diff(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            expected_commit = repo.head.commit.hexsha

            info = read_repo(str(root))
            repo.close()

        self.assertEqual(info["root"], str(root))
        self.assertEqual(info["commit_sha"], expected_commit)
        self.assertIn("value = 2", info["diff"])
        self.assertIn("value = 1", info["diff"])

    def test_truncates_large_diff(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo = self._make_repo(root)
            with patch("router.repo.MAX_DIFF_CHARS", 5):
                info = read_repo(str(root))
            repo.close()

        self.assertEqual(info["diff"], "diff \n...[diff truncated]")

    def test_rejects_path_outside_git_repo(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(NotAGitRepo):
                read_repo(temp_dir)


if __name__ == "__main__":
    unittest.main()
