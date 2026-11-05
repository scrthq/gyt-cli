from pathlib import Path

from typer.testing import CliRunner

from gyt_cli.cli import app
from tests.helpers import advance_origin_trunk, run_git, start_feature

runner = CliRunner()


def test_sync_rebases_onto_origin_base_and_restores_dirty_work(clone: Path):
    start_feature(clone)
    advance_origin_trunk(clone, "upstream\n")
    (clone / "feature.txt").write_text("uncommitted edit\n")
    (clone / "scratch.txt").write_text("untracked\n")

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 0, result.output
    assert "Stashing" in result.output
    run_git(clone, "merge-base", "--is-ancestor", "origin/trunk", "HEAD")
    assert (clone / "README").read_text() == "upstream\n"
    assert (clone / "feature.txt").read_text() == "uncommitted edit\n"
    assert (clone / "scratch.txt").read_text() == "untracked\n"
    assert run_git(clone, "stash", "list") == ""


def test_sync_merge_creates_merge_commit(clone: Path):
    start_feature(clone)
    advance_origin_trunk(clone, "upstream\n")

    result = runner.invoke(app, ["sync", "--merge"])

    assert result.exit_code == 0, result.output
    parents = run_git(clone, "rev-list", "--parents", "-n", "1", "HEAD").split()
    assert len(parents) == 3  # the commit itself plus two parents


def test_sync_conflict_aborts_and_restores_stash(clone: Path):
    start_feature(clone, filename="README")
    before = run_git(clone, "rev-parse", "HEAD")
    advance_origin_trunk(clone, "upstream\n")
    (clone / "scratch.txt").write_text("untracked\n")

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 1
    assert "aborted" in result.output
    assert run_git(clone, "rev-parse", "HEAD") == before
    assert (clone / "scratch.txt").read_text() == "untracked\n"
    assert run_git(clone, "stash", "list") == ""


def test_sync_on_base_branch_fast_forwards(clone: Path):
    advance_origin_trunk(clone, "upstream\n")

    result = runner.invoke(app, ["sync"])

    assert result.exit_code == 0, result.output
    assert run_git(clone, "rev-parse", "HEAD") == run_git(
        clone, "rev-parse", "origin/trunk"
    )


def test_sync_explicit_base_branch(clone: Path):
    start_feature(clone)
    seed = clone.parent / "seed"
    run_git(seed, "checkout", "-b", "develop-local")
    (seed / "dev.txt").write_text("dev\n")
    run_git(seed, "add", ".")
    run_git(seed, "commit", "-m", "dev change")
    run_git(seed, "push", "origin", "develop-local:develop")

    result = runner.invoke(app, ["sync", "develop"])

    assert result.exit_code == 0, result.output
    run_git(clone, "merge-base", "--is-ancestor", "origin/develop", "HEAD")
