import subprocess
from pathlib import Path


def run_git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def commit_file(cwd: Path, filename: str, content: str, message: str) -> str:
    (cwd / filename).write_text(content)
    run_git(cwd, "add", filename)
    run_git(cwd, "commit", "-m", message)
    return run_git(cwd, "rev-parse", "HEAD")


def advance_origin_trunk(work: Path, content: str, filename: str = "README") -> None:
    """Push a new commit to origin/trunk from the seed repo."""
    seed = work.parent / "seed"
    commit_file(seed, filename, content, "upstream change")
    run_git(seed, "push", "origin", "trunk")


def start_feature(
    work: Path,
    filename: str = "feature.txt",
    content: str = "feature\n",
    branch: str = "feature/alive",
    push: bool = True,
) -> None:
    run_git(work, "checkout", "-b", branch)
    commit_file(work, filename, content, "feature change")
    if push:
        run_git(work, "push", "-u", "origin", branch)


def push_and_delete_remote(work: Path, branch: str) -> None:
    """Create a branch, push it, then delete it on the remote (as a merged PR would)."""
    run_git(work, "checkout", "-b", branch)
    run_git(work, "push", "-u", "origin", branch)
    run_git(work, "push", "origin", f":{branch}")


def local_branches(work: Path) -> set[str]:
    return set(run_git(work, "branch", "--format=%(refname:short)").split())


def subjects(work: Path, rev_range: str) -> list[str]:
    out = run_git(work, "log", "--format=%s", rev_range)
    return out.splitlines() if out else []
