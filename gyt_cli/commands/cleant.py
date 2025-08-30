# import subprocess
from typing_extensions import Annotated
import git
import typer

app = typer.Typer(
    help="Cleans up branches that have been merged into main/master.",
)


@app.callback(invoke_without_command=True)
def cleant(
    ctx: typer.Context,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Force cleans the currently checked out branch, even if it is not merged into main",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = git.Repo(".", search_parent_directories=True)
    current_branch = repo.active_branch.name
    current_branch_is_merged = False

    if "main" in repo.heads:
        print("Checking out main...")
        repo.git.checkout("main")
    elif "master" in repo.heads:
        print("Checking out master...")
        repo.git.checkout("master")

    print("Pulling...")
    repo.git.pull()
    print("Pruning...")
    for branch in repo.remote("origin").stale_refs:
        if isinstance(branch, git.refs.remote.RemoteReference):
            type(branch).delete(repo, branch)

    all_branches = git.Git().branch("--all").split()

    # loop through all local branches and check if they are merged into main
    for branch in repo.branches:
        if branch.name == "main" or branch.name == "master":
            continue
        if f"remotes/origin/{branch.name}" not in all_branches or (
            force and current_branch == branch.name
        ):
            print("Deleting %s..." % branch.name)
            repo.git.branch("-D", branch.name)
            if current_branch == branch.name:
                current_branch_is_merged = True
                if force:
                    repo.remote().push(refspec=(":%s" % branch.remote_head))

    if not current_branch_is_merged:
        repo.git.checkout(current_branch)


if __name__ == "__main__":
    app()
