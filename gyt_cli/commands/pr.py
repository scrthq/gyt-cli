from typing import Optional
from urllib.parse import quote

import git
import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    base_branch_or_fail,
    base_ref,
    current_branch,
    fail,
    github_web_url,
    has_upstream,
    is_wip_subject,
    open_repo,
    push_current_branch,
)

app = typer.Typer(
    help="Pushes the current branch if needed and opens GitHub's new pull request page for it.",
)


def _pr_title(repo: git.Repo, target: str) -> Optional[str]:
    """Latest real commit subject since the base; WIP snapshots make poor PR titles."""
    for commit in repo.iter_commits(f"{target}..HEAD", no_merges=True):
        subject = str(commit.summary)
        if not is_wip_subject(subject):
            return subject
    return None


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def pr(
    ctx: typer.Context,
    branch: Annotated[
        Optional[str],
        typer.Argument(
            help="Base branch the pull request targets. Defaults to the remote's default branch.",
            show_default=False,
        ),
    ] = None,
    open_browser: Annotated[
        bool,
        typer.Option("--open/--no-open", help="Open the page in the browser."),
    ] = True,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    current = current_branch(repo)
    base = base_branch_or_fail(repo, branch)
    if current == base:
        fail(f"You are on the base branch {base}; check out a feature branch first.")
    try:
        web_url = github_web_url(repo.remote("origin").url)
    except ValueError as e:
        fail(str(e))

    if not has_upstream(repo) or int(repo.git.rev_list("--count", "@{upstream}..HEAD")):
        print(f"Pushing {current}...")
        push_current_branch(repo, current)

    url = (
        f"{web_url}/compare/{quote(base, safe='/')}...{quote(current, safe='/')}"
        "?expand=1"
    )
    title = _pr_title(repo, base_ref(repo, base))
    if title:
        url += f"&title={quote(title, safe='')}"
    else:
        typer.secho(
            f"No non-WIP commits since {base}, so the title was left blank. "
            "Use a Conventional Commit title.",
            fg=typer.colors.YELLOW,
            err=True,
        )
    print(f"Pull request page: {url}")
    if open_browser:
        typer.launch(url)


if __name__ == "__main__":
    app()
