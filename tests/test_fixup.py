from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import commit_file, run_git, subjects

runner = CliRunner()


def _branch_with_two_commits(clone: Path) -> str:
    run_git(clone, "checkout", "-b", "feature/alive")
    target = commit_file(clone, "a.txt", "a\n", "add a")
    commit_file(clone, "b.txt", "b\n", "add b")
    return target


def test_fixup_folds_staged_changes_into_target_commit(clone: Path):
    target = _branch_with_two_commits(clone)
    (clone / "a.txt").write_text("a fixed\n")
    run_git(clone, "add", "a.txt")

    result = runner.invoke(app, ["fixup", target])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "origin/trunk..HEAD") == ["add b", "add a"]
    assert run_git(clone, "show", "HEAD~1:a.txt") == "a fixed"
    assert run_git(clone, "status", "--porcelain") == ""


def test_fixup_prompts_for_target_when_omitted(clone: Path):
    _branch_with_two_commits(clone)
    (clone / "a.txt").write_text("a fixed\n")
    run_git(clone, "add", "a.txt")

    # Commits are listed newest first: 1 = "add b", 2 = "add a".
    result = runner.invoke(app, ["fixup"], input="2\n")

    assert result.exit_code == 0, result.output
    assert "add a" in result.output
    assert run_git(clone, "show", "HEAD~1:a.txt") == "a fixed"


def test_fixup_keeps_unstaged_changes(clone: Path):
    target = _branch_with_two_commits(clone)
    (clone / "a.txt").write_text("a fixed\n")
    run_git(clone, "add", "a.txt")
    (clone / "b.txt").write_text("unstaged\n")

    result = runner.invoke(app, ["fixup", target])

    assert result.exit_code == 0, result.output
    assert (clone / "b.txt").read_text() == "unstaged\n"


def test_fixup_no_rebase_only_creates_fixup_commit(clone: Path):
    target = _branch_with_two_commits(clone)
    (clone / "a.txt").write_text("a fixed\n")
    run_git(clone, "add", "a.txt")

    result = runner.invoke(app, ["fixup", target, "--no-rebase"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == ["fixup! add a"]


def test_fixup_requires_staged_changes(clone: Path):
    target = _branch_with_two_commits(clone)

    result = runner.invoke(app, ["fixup", target])

    assert result.exit_code == 1
    assert "staged" in result.output
