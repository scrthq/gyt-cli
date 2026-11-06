from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import commit_file, run_git, subjects

runner = CliRunner()


def _three_commit_branch(clone: Path, branch: str = "feature/alive") -> str:
    run_git(clone, "checkout", "-b", branch)
    commit_file(clone, "a.txt", "a\n", "feat: first change")
    commit_file(clone, "b.txt", "b\n", "wip")
    commit_file(clone, "c.txt", "c\n", "more wip")
    return run_git(clone, "rev-parse", "HEAD^{tree}")


def test_squash_combines_branch_commits_using_first_message(clone: Path):
    tree = _three_commit_branch(clone)

    result = runner.invoke(app, ["squash"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "origin/trunk..HEAD") == ["feat: first change"]
    assert run_git(clone, "rev-parse", "HEAD^{tree}") == tree


def test_squash_with_message_applies_conventional_prefix(clone: Path):
    _three_commit_branch(clone, branch="feature/ABC-12-thing")

    result = runner.invoke(app, ["squash", "-m", "do the thing", "--type", "fix"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "origin/trunk..HEAD") == ["fix(ABC-12): do the thing"]


def test_squash_push_force_pushes_with_lease(clone: Path):
    _three_commit_branch(clone)
    run_git(clone, "push", "-u", "origin", "feature/alive")

    result = runner.invoke(app, ["squash", "--push"])

    assert result.exit_code == 0, result.output
    assert run_git(clone, "rev-parse", "HEAD") == run_git(
        clone, "rev-parse", "origin/feature/alive"
    )


def test_squash_refuses_dirty_tree(clone: Path):
    _three_commit_branch(clone)
    (clone / "a.txt").write_text("dirty\n")

    result = runner.invoke(app, ["squash"])

    assert result.exit_code == 1
    assert "uncommitted" in result.output
    assert len(subjects(clone, "origin/trunk..HEAD")) == 3


def test_squash_single_commit_without_message_is_noop(clone: Path):
    run_git(clone, "checkout", "-b", "feature/one")
    commit_file(clone, "a.txt", "a\n", "only one")

    result = runner.invoke(app, ["squash"])

    assert result.exit_code == 0, result.output
    assert "already a single commit" in result.output


def test_squash_with_no_commits_fails(clone: Path):
    run_git(clone, "checkout", "-b", "feature/empty")

    result = runner.invoke(app, ["squash"])

    assert result.exit_code == 1
    assert "No commits" in result.output


def test_squash_skips_wip_commits_when_reusing_a_message(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    commit_file(clone, "a.txt", "a\n", "chore: wip")
    commit_file(clone, "b.txt", "b\n", "feat: real change")
    commit_file(clone, "c.txt", "c\n", "WIP")

    result = runner.invoke(app, ["squash"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "origin/trunk..HEAD") == ["feat: real change"]


def test_squash_all_wip_commits_requires_a_message(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    commit_file(clone, "a.txt", "a\n", "chore: wip")
    commit_file(clone, "b.txt", "b\n", "chore: wip")

    result = runner.invoke(app, ["squash"])

    assert result.exit_code == 1
    assert "pass a message" in result.output
    assert len(subjects(clone, "origin/trunk..HEAD")) == 2


def test_squash_accepts_the_added_commit_types(clone: Path):
    _three_commit_branch(clone)

    result = runner.invoke(app, ["squash", "-m", "speed it up", "--type", "perf"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "origin/trunk..HEAD") == ["perf: speed it up"]
