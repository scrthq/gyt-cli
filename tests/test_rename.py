from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import local_branches, run_git, start_feature

runner = CliRunner()


def _remote_branches(clone: Path) -> set[str]:
    out = run_git(clone, "ls-remote", "--heads", "origin")
    return {line.split("refs/heads/")[1] for line in out.splitlines()}


def test_rename_pushed_branch_renames_remote_and_upstream(clone: Path):
    start_feature(clone, branch="feature/old")

    result = runner.invoke(app, ["rename", "feature/new"])

    assert result.exit_code == 0, result.output
    assert "feature/new" in local_branches(clone)
    assert "feature/old" not in local_branches(clone)
    remote = _remote_branches(clone)
    assert "feature/new" in remote and "feature/old" not in remote
    assert run_git(clone, "rev-parse", "--abbrev-ref", "@{upstream}") == (
        "origin/feature/new"
    )


def test_rename_local_only_branch_does_not_push(clone: Path):
    start_feature(clone, branch="feature/old", push=False)

    result = runner.invoke(app, ["rename", "feature/new"])

    assert result.exit_code == 0, result.output
    assert "feature/new" in local_branches(clone)
    assert "feature/new" not in _remote_branches(clone)


def test_rename_local_flag_skips_remote(clone: Path):
    start_feature(clone, branch="feature/old")

    result = runner.invoke(app, ["rename", "feature/new", "--local"])

    assert result.exit_code == 0, result.output
    assert "feature/old" in _remote_branches(clone)
    assert "feature/new" not in _remote_branches(clone)


def test_rename_refuses_existing_target(clone: Path):
    start_feature(clone, branch="feature/old", push=False)

    result = runner.invoke(app, ["rename", "trunk"])

    assert result.exit_code == 1
    assert "already exists" in result.output
    assert run_git(clone, "branch", "--show-current") == "feature/old"
