from typing import Optional

from typing_extensions import Annotated
import git
import typer

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    PROTECTED_BRANCHES,
    base_branch_or_fail,
    gone_branches,
    open_repo,
    rebase_or_abort,
    worktree_branches,
)

app = typer.Typer(
    help="Pulls the default branch (or a given base branch) and deletes local branches whose upstream was deleted on origin.",
)


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def cleant(
    ctx: typer.Context,
    branch: Annotated[
        Optional[str],
        typer.Argument(
            help="Base branch to clean against and pull. Defaults to the remote's default branch.",
            show_default=False,
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Force cleans the currently checked out branch, even if it is not merged into the base branch",
        ),
    ] = False,
    all_missing: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Also delete local branches that were never pushed to origin, not just ones whose upstream is gone.",
        ),
    ] = False,
    rebase: Annotated[
        bool,
        typer.Option(
            "--rebase",
            "-r",
            help="Rebase the current branch onto the freshly pulled base branch. Aborts cleanly on conflict.",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current_branch = repo.active_branch.name
    current_branch_is_merged = False
    base_branch = base_branch_or_fail(repo, branch)

    # Clean up worktrees before branches: a branch checked out in a stale
    # worktree cannot be deleted until its worktree record is pruned.
    # `git worktree prune -v` reports what it removes on stderr.
    print("Pruning worktrees...")
    _, _, pruned_worktrees = repo.git.worktree("prune", "-v", with_extended_output=True)
    if pruned_worktrees:
        print(pruned_worktrees)

    print(f"Checking out {base_branch}...")
    repo.git.checkout(base_branch)

    print("Pulling...")
    repo.git.pull()
    print("Pruning...")
    for stale in repo.remote("origin").stale_refs:
        if isinstance(stale, git.refs.remote.RemoteReference):
            type(stale).delete(repo, stale)

    if all_missing:
        # Anything without a matching branch on origin, including never-pushed branches.
        remote_branches = {ref.remote_head for ref in repo.remote("origin").refs}
        to_delete = {b.name for b in repo.branches if b.name not in remote_branches}
    else:
        # Only branches whose upstream was deleted on origin (typically merged PRs).
        to_delete = gone_branches(repo)
    protected = PROTECTED_BRANCHES | {base_branch}
    # git refuses to delete a branch checked out in another worktree.
    in_worktrees = worktree_branches(repo)

    for local in repo.branches:
        if local.name in protected:
            continue
        if local.name in to_delete or (force and current_branch == local.name):
            if local.name in in_worktrees:
                print(
                    f"Skipping {local.name} (checked out in worktree at "
                    f"{in_worktrees[local.name]})..."
                )
                continue
            print("Deleting %s..." % local.name)
            try:
                repo.git.branch("-D", local.name)
            except git.GitCommandError as e:
                # Report and keep going so we still return to the original branch.
                typer.secho(
                    f"Could not delete {local.name}: {e.stderr.strip()}",
                    fg=typer.colors.YELLOW,
                    err=True,
                )
                continue
            if current_branch == local.name:
                current_branch_is_merged = True
                if force:
                    repo.remote().push(refspec=(":%s" % local.remote_head))

    if not current_branch_is_merged:
        repo.git.checkout(current_branch)
        if rebase and current_branch != base_branch:
            print(f"Rebasing {current_branch} onto {base_branch}...")
            rebase_or_abort(repo, base_branch)


if __name__ == "__main__":
    app()
