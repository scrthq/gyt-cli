# import subprocess
# import git
# import re
# from typing_extensions import Annotated

import git
import os
import typer

app = typer.Typer()


@app.callback(
    invoke_without_command=True,
    help="Opens the current branch in GitHub in the browser. Currently only supports GitHub.",
)
def open():
    repo = git.Repo(os.getcwd(), search_parent_directories=True)
    current_branch = repo.active_branch.name

    url = (
        repo.remote()
        .url.replace(".git", "")
        .replace("git@github.com:", "https://github.com/")
        + f"/tree/{current_branch}"
    )
    print(f"Opening {url} in browser...")
    typer.launch(url)


if __name__ == "__main__":
    app()
