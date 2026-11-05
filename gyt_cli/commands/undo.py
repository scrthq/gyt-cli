import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    current_branch,
    fail,
    is_pushed,
    open_repo,
)

app = typer.Typer(
    help="Undoes the last commit, keeping its changes staged. Refuses if the commit is already pushed.",
)


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def undo(
    ctx: typer.Context,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Undo the commit even if it has already been pushed.",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current_branch(repo)
    try:
        head = repo.head.commit
    except ValueError:
        fail("There are no commits to undo.")
    if not head.parents:
        fail("Cannot undo the first commit in the repository.")

    subject = str(head.summary)
    pushed = is_pushed(repo, "HEAD")
    if pushed and not force:
        fail(
            f"'{subject}' is already pushed. Undoing it rewrites shared history; "
            "re-run with --force to undo it anyway."
        )

    repo.git.reset("--soft", "HEAD~1")
    print(f"Undid commit {head.hexsha[:7]} '{subject}'. Its changes are still staged.")
    if pushed:
        print(
            "The commit is still on the remote. Push with "
            "`git push --force-with-lease` to remove it there."
        )


if __name__ == "__main__":
    app()
