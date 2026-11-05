from typing import Optional

import git
import typer
from typing_extensions import Annotated

from gyt_cli.commands.camp import CommitTypes
from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    base_branch_or_fail,
    base_ref,
    conventional_prefix,
    current_branch,
    fail,
    has_upstream,
    is_dirty,
    open_repo,
    push_current_branch,
)

app = typer.Typer(
    help="Squashes every commit on the current branch since it left the base branch into one commit.",
)


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def squash(
    ctx: typer.Context,
    branch: Annotated[
        Optional[str],
        typer.Argument(
            help="Base branch the current branch was created from. Defaults to the remote's default branch.",
            show_default=False,
        ),
    ] = None,
    message: Annotated[
        Optional[str],
        typer.Option(
            "--message",
            "-m",
            help="Message for the squashed commit, formatted like `gyt camp`. Defaults to the branch's first commit message.",
            show_default=False,
        ),
    ] = None,
    type: Annotated[
        CommitTypes,
        typer.Option(help="Commit type used with --message."),
    ] = CommitTypes.FEAT,
    scope: Annotated[
        Optional[str],
        typer.Option(
            help="Commit scope used with --message. Defaults to Jira keys found in the branch name.",
            show_default=False,
        ),
    ] = None,
    push: Annotated[
        bool,
        typer.Option(
            "--push",
            "-p",
            help="Push the squashed branch with --force-with-lease.",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current = current_branch(repo)
    base = base_branch_or_fail(repo, branch)
    if current == base:
        fail(f"You are on the base branch {base}; check out a feature branch first.")
    if is_dirty(repo):
        fail("You have uncommitted changes; commit or stash them before squashing.")

    target = base_ref(repo, base)
    merge_base = repo.git.merge_base(target, "HEAD")
    commits = repo.git.rev_list("--reverse", f"{merge_base}..HEAD").splitlines()
    if not commits:
        fail(f"No commits on {current} since it branched from {target}.")
    if len(commits) == 1 and not message:
        print(f"{current} is already a single commit on top of {target}.")
        return

    if message:
        new_message = f"{conventional_prefix(type.value, scope, current)}: {message}"
    else:
        new_message = repo.git.log("-1", "--format=%B", commits[0])

    original_head = repo.head.commit.hexsha
    repo.git.reset("--soft", merge_base)
    try:
        repo.git.commit("-m", new_message)
    except git.GitCommandError as e:
        # e.g. a commit hook rejected it: put the branch back exactly as it was.
        repo.git.reset("--soft", original_head)
        fail(f"Commit failed, so the branch was left unchanged:\n{e.stderr.strip()}")

    print(f"Squashed {len(commits)} commits into: {new_message.splitlines()[0]}")
    if push:
        print(f"Pushing {current} with --force-with-lease...")
        push_current_branch(repo, current, "--force-with-lease")
    elif has_upstream(repo):
        print(
            "The branch was already pushed; update it with `git push --force-with-lease`."
        )


if __name__ == "__main__":
    app()
