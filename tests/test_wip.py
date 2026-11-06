from pathlib import Path

import pytest
from typer.testing import CliRunner

from gyt_cli.cli import app
from gyt_cli.git_ops import WIP_SUBJECT, is_wip_subject
from tests.helpers import commit_file, run_git, subjects

runner = CliRunner()


def test_wip_commits_everything_and_pushes_with_upstream(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    (clone / "README").write_text("edited\n")
    (clone / "new.txt").write_text("untracked\n")

    result = runner.invoke(app, ["wip"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == ["chore: wip"]
    assert run_git(clone, "status", "--porcelain") == ""
    assert run_git(clone, "rev-parse", "HEAD") == run_git(
        clone, "rev-parse", "origin/feature/alive"
    )


def test_wip_no_push(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    (clone / "new.txt").write_text("x\n")

    result = runner.invoke(app, ["wip", "--no-push"])

    assert result.exit_code == 0, result.output
    assert subjects(clone, "-1") == ["chore: wip"]
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


def test_unwip_undoes_what_wip_wrote_and_older_wip_commits(clone: Path):
    run_git(clone, "checkout", "-b", "feature/alive")
    base = commit_file(clone, "real.txt", "real\n", "feat: real work")
    commit_file(clone, "old.txt", "old\n", "WIP")
    (clone / "new.txt").write_text("new\n")
    assert runner.invoke(app, ["wip", "--no-push"]).exit_code == 0

    result = runner.invoke(app, ["unwip"])

    assert result.exit_code == 0, result.output
    assert "2 WIP commit" in result.output
    assert run_git(clone, "rev-parse", "HEAD") == base


@pytest.mark.parametrize(
    "subject, expected",
    [
        (WIP_SUBJECT, True),
        ("WIP", True),
        ("wip: trying something", True),
        ("chore(ui): wip layout", True),
        ("Wipe the cache", False),
        ("chore: wipe the cache", False),
        ("feat: add wip command", False),
    ],
)
def test_is_wip_subject(subject: str, expected: bool):
    assert is_wip_subject(subject) is expected
