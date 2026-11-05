from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import commit_file, run_git, start_feature

runner = CliRunner()


def test_undo_unpushed_commit_keeps_changes_staged(clone: Path):
    start_feature(clone)
    parent = run_git(clone, "rev-parse", "HEAD")
    commit_file(clone, "oops.txt", "oops\n", "oops commit")

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 0, result.output
    assert "oops commit" in result.output
    assert run_git(clone, "rev-parse", "HEAD") == parent
    assert run_git(clone, "diff", "--cached", "--name-only") == "oops.txt"


def test_undo_refuses_pushed_commit(clone: Path):
    start_feature(clone)
    before = run_git(clone, "rev-parse", "HEAD")

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 1
    assert "already pushed" in result.output
    assert run_git(clone, "rev-parse", "HEAD") == before


def test_undo_force_allows_pushed_commit(clone: Path):
    start_feature(clone)

    result = runner.invoke(app, ["undo", "--force"])

    assert result.exit_code == 0, result.output
    assert "force-with-lease" in result.output
    assert run_git(clone, "diff", "--cached", "--name-only") == "feature.txt"


def test_undo_refuses_root_commit(tmp_path: Path, monkeypatch):
    repo = tmp_path / "solo"
    run_git(tmp_path, "init", "-b", "trunk", str(repo))
    commit_file(repo, "a.txt", "a\n", "root")
    monkeypatch.chdir(repo)

    result = runner.invoke(app, ["undo"])

    assert result.exit_code == 1
    assert "first commit" in result.output
