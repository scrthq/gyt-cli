import git
import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    current_branch,
    fail,
    open_repo,
    remote_branch_exists,
)

app = typer.Typer(
    help="Renames the current branch locally and on origin, and points its upstream at the new name.",
)


@app.callback(
    invoke_without_command=True,
    context_settings=COMMAND_CONTEXT_SETTINGS,
    no_args_is_help=True,
)
def rename(
    new_name: Annotated[
        str,
        typer.Argument(help="New name for the current branch."),
    ],
    local: Annotated[
        bool,
        typer.Option(
            "--local",
            "-l",
            help="Only rename the local branch; leave origin untouched.",
        ),
    ] = False,
):
    repo = open_repo()
    old_name = current_branch(repo)
    if new_name == old_name:
        fail(f"The current branch is already named {old_name}.")
    try:
        repo.git.check_ref_format("--branch", new_name)
    except git.GitCommandError:
        fail(f"'{new_name}' is not a valid branch name.")
    if new_name in repo.heads:
        fail(f"Branch '{new_name}' already exists locally.")

    rename_remote = remote_branch_exists(repo, old_name) and not local
    if rename_remote and remote_branch_exists(repo, new_name):
        fail(f"Branch '{new_name}' already exists on origin.")

    repo.git.branch("-m", old_name, new_name)
    print(f"Renamed {old_name} to {new_name} locally.")
    if not rename_remote:
        return

    # Push the new name before deleting the old one, so the work is never only local.
    try:
        print(f"Pushing {new_name} to origin...")
        repo.git.push("-u", "origin", new_name)
        print(f"Deleting {old_name} from origin...")
        repo.git.push("origin", "--delete", old_name)
    except git.GitCommandError as e:
        fail(f"Renaming on origin failed:\n{e.stderr.strip()}")
    print(f"Renamed origin/{old_name} to origin/{new_name}.")


if __name__ == "__main__":
    app()
