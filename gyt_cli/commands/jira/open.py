import git
import re
from typing_extensions import Annotated
import typer

from gyt_cli.utils import load_config

def open_jira(
    ctx: typer.Context,
    extra: Annotated[
        list[str],
        typer.Option(
            help="List of additional Jira issues to open",
        ),
    ] = [],
):
    if ctx.invoked_subcommand is not None:
        return
    """Opens the JIRA ticket in the browser for the current branch.
    """
    gyt_config = load_config()

    current_branch = git.Repo(search_parent_directories=True).active_branch.name
    jira_pattern = re.compile(r"([A-Z]+\-\d+)")

    found = extra + [m.group(0) for m in jira_pattern.finditer(current_branch)]

    if len(found) > 0:
        for j in found:
            try:
                search_url = gyt_config.jira.get_issue_url(j)
                print(f"Opening {search_url}")
                typer.launch(search_url)
            except ValueError as exc:
                raise typer.Abort(exc)
    else:
        raise typer.Abort("No Jira ticket found in current branch and no additional values passed into --issues.")
