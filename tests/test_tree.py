from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import run_git, start_feature

runner = CliRunner()


def test_tree_checks_out_remote_branch_in_sibling_directory(clone: Path):
    start_feature(clone, branch="feature/review-me")
    run_git(clone, "checkout", "trunk")
    run_git(clone, "branch", "-D", "feature/review-me")

    result = runner.invoke(app, ["tree", "feature/review-me"])

    assert result.exit_code == 0, result.output
    path = clone.parent / "work-feature-review-me"
    assert (path / "feature.txt").read_text() == "feature\n"
    assert run_git(path, "branch", "--show-current") == "feature/review-me"
    assert run_git(path, "rev-parse", "--abbrev-ref", "@{upstream}") == (
        "origin/feature/review-me"
    )
    assert str(path) in result.output


def test_tree_creates_new_branch_from_base(clone: Path):
    result = runner.invoke(app, ["tree", "feature/brand-new"])

    assert result.exit_code == 0, result.output
    path = clone.parent / "work-feature-brand-new"
    assert run_git(path, "branch", "--show-current") == "feature/brand-new"
    assert run_git(path, "rev-parse", "HEAD") == run_git(
        clone, "rev-parse", "origin/trunk"
    )


def test_tree_custom_path(clone: Path, tmp_path: Path):
    target = tmp_path / "elsewhere"

    result = runner.invoke(app, ["tree", "develop", "--path", str(target)])

    assert result.exit_code == 0, result.output
    assert run_git(target, "branch", "--show-current") == "develop"


def test_tree_refuses_existing_path(clone: Path):
    (clone.parent / "work-develop").mkdir()

    result = runner.invoke(app, ["tree", "develop"])

    assert result.exit_code == 1
    assert "already exists" in result.output
