from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import commit_file, run_git, subjects

runner = CliRunner()


def test_wip_commits_everything_and_pushes_with_upstream(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    (clone / "README").write_text("edited\n")
    (clone / "new.txt").write_text("untracked\n")

    result = runner.invoke(app, ["wip"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == ["WIP"]
    assert run_git(clone, "status", "--porcelain") == ""
    assert run_git(clone, "rev-parse", "HEAD") == run_git(
        clone, "rev-parse", "origin/feature/alive"
    )


def test_wip_no_push(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    (clone / "new.txt").write_text("x\n")

    result = runner.invoke(app, ["wip", "--no-push"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == ["WIP"]
    assert "origin/feature/alive" not in run_git(clone, "branch", "-r")


def test_wip_with_nothing_to_commit(clone: Path):
    result = runner.invoke(app, ["wip"])

    assert result.exit_code == 0, result.output
    assert "Nothing to commit" in result.output


def test_unwip_restores_consecutive_wip_commits_as_uncommitted_changes(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    base = commit_file(clone, "real.txt", "real\n", "real work")
    commit_file(clone, "a.txt", "a\n", "WIP")
    commit_file(clone, "b.txt", "b\n", "WIP")

    result = runner.invoke(app, ["unwip"])

    assert result.exit_code == 0, result.output
    assert "2 WIP commit" in result.output
    assert run_git(clone, "rev-parse", "HEAD") == base
    status = run_git(clone, "status", "--porcelain")
    assert "a.txt" in status and "b.txt" in status


def test_unwip_refuses_when_last_commit_is_not_wip(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    before = commit_file(clone, "real.txt", "real\n", "real work")

    result = runner.invoke(app, ["unwip"])

    assert result.exit_code == 1
    assert "not a WIP commit" in result.output
    assert run_git(clone, "rev-parse", "HEAD") == before
