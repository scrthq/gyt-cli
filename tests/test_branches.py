from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import commit_file, push_and_delete_remote, run_git, start_feature

runner = CliRunner()


def _row(output: str, branch: str) -> str:
    return next(line for line in output.splitlines() if f" {branch} " in f"{line} ")


def test_branches_reports_ahead_behind_and_upstream_state(clone: Path):
    push_and_delete_remote(clone, "feature/gone")
    run_git(clone, "checkout", "trunk")
    start_feature(clone)
    commit_file(clone, "two.txt", "2\n", "second")
    run_git(clone, "checkout", "trunk")
    run_git(clone, "checkout", "-b", "local-only")

    result = runner.invoke(app, ["branches"])

    assert result.exit_code == 0, result.output
    assert "trunk" in result.output
    gone = _row(result.output, "feature/gone")
    assert "gone" in gone
    alive = _row(result.output, "feature/alive")
    assert "+2" in alive and "-0" in alive
    assert "ahead 1" in alive  # one commit not yet pushed
    local = _row(result.output, "local-only")
    assert local.lstrip().startswith("*")
    assert "no upstream" in local


def test_branches_against_explicit_base(clone: Path):
    start_feature(clone)

    result = runner.invoke(app, ["branches", "develop"])

    assert result.exit_code == 0, result.output
    assert "vs develop" in result.output
