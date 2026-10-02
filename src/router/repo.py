"""Step 4: read the git repo and current diff (read-only, no analysis yet)."""
from git import InvalidGitRepositoryError, Repo

MAX_DIFF_CHARS = 8000  # keep context (and cost) bounded; Phase 3 replaces this


class NotAGitRepo(Exception):
    pass


def read_repo(path: str = ".") -> dict:
    try:
        repo = Repo(path, search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise NotAGitRepo(f"'{path}' is not inside a git repository")

    try:
        root = repo.working_tree_dir
        if not repo.head.is_valid():  # repo with zero commits
            return {"root": root, "commit_sha": None, "diff": ""}

        diff = repo.git.diff("HEAD")  # staged + unstaged changes vs last commit
        if len(diff) > MAX_DIFF_CHARS:
            diff = diff[:MAX_DIFF_CHARS] + "\n...[diff truncated]"
        return {"root": root, "commit_sha": repo.head.commit.hexsha, "diff": diff}
    finally:
        repo.close()
