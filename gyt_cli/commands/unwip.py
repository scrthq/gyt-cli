import typer

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    current_branch,
    fail,
    is_pushed,
    is_wip_subject,
    open_repo,
)

app = typer.Typer(
    help="Turns the WIP commits on top of the branch back into uncommitted changes.",
)


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def unwip(ctx: typer.Context):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current_branch(repo)
    try:
        commit = repo.head.commit
    except ValueError:
        fail("There are no commits yet.")

    # Count consecutive WIP commits from HEAD, never resetting past the root commit.
    count = 0
    while commit.parents and is_wip_subject(str(commit.summary)):
        count += 1
        commit = commit.parents[0]
    if count == 0:
        fail("The last commit is not a WIP commit; nothing to undo.")

    pushed = is_pushed(repo, "HEAD")
    repo.git.reset("--mixed", f"HEAD~{count}")
    print(f"Undid {count} WIP commit(s); the changes are back in your working tree.")
    if pushed:
        print(
            "The WIP commits are still on the remote; your next push will need "
            "`git push --force-with-lease`."
        )


if __name__ == "__main__":
    app()
