import subprocess
import git
import re
import typer
from typing_extensions import Annotated

app = typer.Typer(
    help="Starts a fresh feature branch and syncs with the remote.",
)
@app.callback(invoke_without_command=True, no_args_is_help=True)
def fresh(
    branch:  Annotated[
        str,
        typer.Argument(
            help="Name of the feature branch to be created.",
        )
    ],
):
    repo = git.Repo(search_parent_directories=True)
    rgit: git.Git = repo.git
    rgit.checkout('HEAD', b=branch)
    rgit.push('origin', '-u', branch)

if __name__ == "__main__":
    app()
