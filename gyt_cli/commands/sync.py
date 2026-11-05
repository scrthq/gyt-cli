from typing import Optional

import git
import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    base_branch_or_fail,
    base_ref,
    current_branch,
    fail,
    is_dirty,
    merge_or_abort,
    open_repo,
    rebase_or_abort,
)

app = typer.Typer(
    help="Updates the current branch with the latest base branch, stashing and restoring uncommitted work.",
)


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def sync(
    ctx: typer.Context,
    branch: Annotated[
        Optional[str],
        typer.Argument(
            help="Base branch to sync with. Defaults to the remote's default branch.",
            show_default=False,
        ),
    ] = None,
    merge: Annotated[
        bool,
        typer.Option(
            "--merge",
            "-m",
            help="Merge the base branch in instead of rebasing onto it.",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current = current_branch(repo)
    base = base_branch_or_fail(repo, branch)

    print("Fetching origin...")
    repo.git.fetch("origin", "--prune")
    target = base_ref(repo, base)

    stashed = False
    if is_dirty(repo):
        print("Stashing uncommitted changes...")
        repo.git.stash("push", "--include-untracked", "-m", "gyt sync autostash")
        stashed = True

    try:
        if current == base:
            print(f"Fast-forwarding {current} to {target}...")
            try:
                repo.git.merge("--ff-only", target)
            except git.GitCommandError:
                fail(
                    f"{current} has diverged from {target} and cannot be fast-forwarded."
                )
        elif merge:
            print(f"Merging {target} into {current}...")
            merge_or_abort(repo, target)
        else:
            print(f"Rebasing {current} onto {target}...")
            rebase_or_abort(repo, target)
    finally:
        # Runs on success and on failure, so stashed work is never left behind.
        if stashed:
            _restore_stash(repo)

    print(f"{current} is up to date with {target}.")


def _restore_stash(repo: git.Repo) -> None:
    print("Restoring stashed changes...")
    try:
        repo.git.stash("pop")
    except git.GitCommandError:
        typer.secho(
            "Stashed changes could not be reapplied cleanly. They are still saved: "
            "resolve the conflicts, then run `git stash drop` (see `git stash list`).",
            fg=typer.colors.YELLOW,
            err=True,
        )


if __name__ == "__main__":
    app()
