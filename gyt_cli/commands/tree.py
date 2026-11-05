from pathlib import Path
from typing import Optional

import git
import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    base_branch_or_fail,
    base_ref,
    fail,
    open_repo,
    remote_branch_exists,
)

app = typer.Typer(
    help="Checks out a branch in a new worktree next to the repo, so you can work on it without stashing.",
)


@app.callback(
    invoke_without_command=True,
    context_settings=COMMAND_CONTEXT_SETTINGS,
    no_args_is_help=True,
)
def tree(
    branch: Annotated[
        str,
        typer.Argument(
            help="Branch to check out. Existing local or origin branches are used; otherwise it is created from the base branch."
        ),
    ],
    path: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            "-p",
            help="Where to create the worktree. Defaults to <repo>-<branch> next to the repo.",
            show_default=False,
        ),
    ] = None,
    from_branch: Annotated[
        Optional[str],
        typer.Option(
            "--from",
            help="Base branch for a new branch. Defaults to the remote's default branch.",
            show_default=False,
        ),
    ] = None,
):
    repo = open_repo()
    root = Path(str(repo.working_tree_dir))
    target = (path or root.parent / f"{root.name}-{branch.replace('/', '-')}").resolve()
    if target.exists():
        fail(f"{target} already exists.")

    if branch in repo.heads:
        args = [str(target), branch]
    elif remote_branch_exists(repo, branch):
        args = ["--track", "-b", branch, str(target), f"origin/{branch}"]
    else:
        start = base_ref(repo, base_branch_or_fail(repo, from_branch))
        # --no-track: the new branch must not adopt the base branch as its upstream.
        args = ["--no-track", "-b", branch, str(target), start]
        print(f"Creating new branch {branch} from {start}...")

    try:
        repo.git.worktree("add", *args)
    except git.GitCommandError as e:
        fail(f"Could not create the worktree:\n{e.stderr.strip()}")
    print(f"Created worktree for {branch} at {target}")
    print(f"  cd {target}")


if __name__ == "__main__":
    app()
