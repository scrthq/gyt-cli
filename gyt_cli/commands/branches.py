from typing import Optional

import typer
from typing_extensions import Annotated

from gyt_cli.git_ops import (
    COMMAND_CONTEXT_SETTINGS,
    base_branch_or_fail,
    base_ref,
    open_repo,
)

app = typer.Typer(
    help="Lists local branches with ahead/behind counts against the base branch and their upstream state.",
)


def _upstream_state(upstream: str, track: str) -> str:
    """Describe the upstream: `no upstream`, `gone`, `up to date`, or `ahead 1, behind 2`."""
    if not upstream:
        return "no upstream"
    if track == "[gone]":
        return "gone"
    return track.strip("[]") or "up to date"


@app.callback(invoke_without_command=True, context_settings=COMMAND_CONTEXT_SETTINGS)
def branches(
    ctx: typer.Context,
    branch: Annotated[
        Optional[str],
        typer.Argument(
            help="Base branch to compare against. Defaults to the remote's default branch.",
            show_default=False,
        ),
    ] = None,
    fetch: Annotated[
        bool,
        typer.Option(
            "--fetch",
            "-f",
            help="Fetch and prune origin first, so branches deleted on the remote show as gone.",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is not None:
        return
    repo = open_repo()
    base = base_branch_or_fail(repo, branch)
    if fetch:
        print("Fetching origin...")
        repo.git.fetch("origin", "--prune")
    target = base_ref(repo, base)
    current = None if repo.head.is_detached else repo.active_branch.name

    refs = repo.git.for_each_ref(
        "--format=%(refname:short)%09%(upstream:short)%09%(upstream:track)%09%(committerdate:relative)",
        "refs/heads",
    ).splitlines()

    rows = []
    for line in refs:
        name, upstream, track, date = line.split("\t")
        # Left side counts commits only in the base (behind), right side only in the branch (ahead).
        behind, ahead = repo.git.rev_list(
            "--left-right", "--count", f"{target}...{name}"
        ).split()
        rows.append(
            (
                "*" if name == current else " ",
                name,
                f"+{ahead} -{behind}",
                _upstream_state(upstream, track),
                date,
            )
        )

    print(f"Ahead/behind vs {base} ({target}):")
    widths = [max(len(row[i]) for row in rows) for i in range(1, 4)]
    for marker, name, counts, state, date in rows:
        print(
            f"{marker} {name:<{widths[0]}}  {counts:<{widths[1]}}  "
            f"{state:<{widths[2]}}  {date}"
        )


if __name__ == "__main__":
    app()
