import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    PROTECTED_BRANCHES,
    WIP_SUBJECT,
    current_branch,
    fail,
    is_dirty,
    open_repo,
    push_current_branch,
    resolve_base_branch,
)

app = typer.Typer(
    help="Commits everything (including untracked files) as a WIP commit and pushes it. Undo with `gyt unwip`.",
)


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def wip(
    ctx: typer.Context,
    push: Annotated[
        bool,
        typer.Option("--push/--no-push", help="Push the WIP commit."),
    ] = True,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    branch = current_branch(repo)
    if not is_dirty(repo):
        print("Nothing to commit; the working tree is clean.")
        return

    protected = set(PROTECTED_BRANCHES)
    try:
        protected.add(resolve_base_branch(repo))
    except ValueError:
        pass
    if branch in protected:
        fail(f"Refusing to WIP-commit on {branch}; switch to a feature branch first.")

    repo.git.add("--all")
    # --no-verify: a WIP snapshot should not be blocked by lint/test hooks.
    repo.git.commit("--no-verify", "-m", WIP_SUBJECT)
    print("Committed all changes as a WIP commit.")
    if push:
        print(f"Pushing {branch}...")
        push_current_branch(repo, branch)


if __name__ == "__main__":
    app()
