from pathlib import Path

import git
import pytest
from typer.testing import CliRunner

from gyt_cli.cli import app
from gyt_cli.git_ops import resolve_base_branch
from tests.helpers import (
    advance_origin_trunk,
    local_branches,
    push_and_delete_remote,
    run_git,
    start_feature,
)

runner = CliRunner()


def test_resolve_base_branch_uses_remote_default(clone: Path):
    assert resolve_base_branch(git.Repo(clone)) == "trunk"


def test_resolve_base_branch_falls_back_to_main_when_origin_head_missing(clone: Path):
    run_git(clone, "branch", "main")
    run_git(clone, "remote", "set-head", "origin", "--delete")
    assert resolve_base_branch(git.Repo(clone)) == "main"


def test_resolve_base_branch_explicit_branch(clone: Path):
    assert resolve_base_branch(git.Repo(clone), "develop") == "develop"


def test_resolve_base_branch_unknown_branch_raises(clone: Path):
    with pytest.raises(ValueError, match="nope"):
        resolve_base_branch(git.Repo(clone), "nope")


def test_cleant_defaults_to_remote_default_branch(clone: Path):
    push_and_delete_remote(clone, "feature/gone")
    run_git(clone, "checkout", "trunk")
    run_git(clone, "checkout", "-b", "feature/alive")
    run_git(clone, "push", "-u", "origin", "feature/alive")

    result = runner.invoke(app, ["cleant"])

    assert result.exit_code == 0, result.output
    assert "Checking out trunk..." in result.output
    assert local_branches(clone) == {"trunk", "feature/alive"}
    assert run_git(clone, "branch", "--show-current") == "feature/alive"


def test_cleant_with_explicit_branch_checks_out_and_protects_it(clone: Path):
    push_and_delete_remote(clone, "feature/gone")

    result = runner.invoke(app, ["cleant", "develop"])

    assert result.exit_code == 0, result.output
    assert "Checking out develop..." in result.output
    # The current branch was deleted, so we land on the requested base branch.
    assert run_git(clone, "branch", "--show-current") == "develop"
    assert local_branches(clone) == {"trunk", "develop"}


def test_cleant_unknown_branch_exits_with_error(clone: Path):
    result = runner.invoke(app, ["cleant", "nope"])

    assert result.exit_code == 1
    assert "nope" in result.output


def test_cleant_rebase_rebases_current_branch_onto_updated_base(clone: Path):
    start_feature(clone)
    advance_origin_trunk(clone, "upstream\n")

    result = runner.invoke(app, ["cleant", "--rebase"])

    assert result.exit_code == 0, result.output
    assert "Rebasing feature/alive onto trunk..." in result.output
    assert run_git(clone, "branch", "--show-current") == "feature/alive"
    # The updated trunk is now an ancestor of the feature branch.
    run_git(clone, "merge-base", "--is-ancestor", "trunk", "HEAD")
    assert (clone / "README").read_text() == "upstream\n"


def test_cleant_without_rebase_leaves_branch_untouched(clone: Path):
    start_feature(clone)
    before = run_git(clone, "rev-parse", "HEAD")
    advance_origin_trunk(clone, "upstream\n")

    result = runner.invoke(app, ["cleant"])

    assert result.exit_code == 0, result.output
    assert run_git(clone, "rev-parse", "HEAD") == before


def test_cleant_rebase_conflict_aborts_and_exits_with_error(clone: Path):
    start_feature(clone, filename="README")
    before = run_git(clone, "rev-parse", "HEAD")
    advance_origin_trunk(clone, "upstream\n")

    result = runner.invoke(app, ["cleant", "--rebase"])

    assert result.exit_code == 1
    assert "aborted" in result.output
    assert run_git(clone, "branch", "--show-current") == "feature/alive"
    assert run_git(clone, "rev-parse", "HEAD") == before
    assert not (clone / ".git" / "rebase-merge").exists()


def test_cleant_rebase_skipped_when_current_branch_was_cleaned(clone: Path):
    push_and_delete_remote(clone, "feature/gone")

    result = runner.invoke(app, ["cleant", "--rebase"])

    assert result.exit_code == 0, result.output
    assert "Rebasing" not in result.output
    assert run_git(clone, "branch", "--show-current") == "trunk"


def test_cleant_accepts_options_after_branch_argument(clone: Path):
    start_feature(clone)
    advance_origin_trunk(clone, "upstream\n")
    run_git(clone, "push", "origin", "origin/trunk:refs/heads/develop", "--force")
    run_git(clone, "fetch", "origin")

    result = runner.invoke(app, ["cleant", "develop", "--rebase"])

    assert result.exit_code == 0, result.output
    assert "Rebasing feature/alive onto develop..." in result.output


def test_cleant_skips_branch_checked_out_in_another_worktree(clone: Path):
    push_and_delete_remote(clone, "feature/in-tree")
    run_git(clone, "checkout", "trunk")
    start_feature(clone)
    run_git(clone, "worktree", "add", str(clone.parent / "wt"), "feature/in-tree")

    result = runner.invoke(app, ["cleant"])

    assert result.exit_code == 0, result.output
    assert "Skipping feature/in-tree" in result.output
    assert "feature/in-tree" in local_branches(clone)
    assert run_git(clone, "branch", "--show-current") == "feature/alive"


def test_cleant_keeps_never_pushed_branches_by_default(clone: Path):
    start_feature(clone, branch="feature/unpushed", push=False)
    run_git(clone, "checkout", "trunk")
    push_and_delete_remote(clone, "feature/gone")

    result = runner.invoke(app, ["cleant"])

    assert result.exit_code == 0, result.output
    assert local_branches(clone) == {"trunk", "feature/unpushed"}


def test_cleant_all_also_deletes_branches_missing_from_origin(clone: Path):
    start_feature(clone, branch="feature/unpushed", push=False)
    run_git(clone, "checkout", "trunk")
    start_feature(clone, branch="feature/alive")

    result = runner.invoke(app, ["cleant", "--all"])

    assert result.exit_code == 0, result.output
    assert "Deleting feature/unpushed..." in result.output
    assert local_branches(clone) == {"trunk", "feature/alive"}
