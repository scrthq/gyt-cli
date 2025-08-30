# import subprocess
# import git
# import re
# from typing_extensions import Annotated
import typer
import enum
import subprocess
import sys
import re
from typing_extensions import Annotated

from gyt_cli.config.model import CommitConfig, GytCliConfig, JiraConfig

app = typer.Typer()


try:
    import git
except ModuleNotFoundError:
    subprocess.run([sys.executable, "-m", "pip", "install", "gitpython"])
    import git

try:
    import typer
except ModuleNotFoundError:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "typer",
            "rich",
            "shellingham",
        ]
    )
    import typer


app = typer.Typer()


class CommitTypes(str, enum.Enum):
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    CI = "ci"


@app.callback(
    invoke_without_command=True,
    no_args_is_help=True,
    help="Commands to help with commit message generation and management. Prioritizes Conventional Commit format in a way that also supports Atlassian Smart Commits for issue commenting and time tracking via commit messages.",
)
def camp(
    ctx: typer.Context,
    message: Annotated[
        str,
        typer.Argument(
            help="Commit message",
        ),
    ],
    all: Annotated[
        bool,
        typer.Option(
            help="Includes '--all' if true. Defaults to true.",
        ),
    ] = True,
    body: Annotated[
        str | None,
        typer.Option(
            help="Commit message body",
        ),
    ] = None,
    breaking_changes: Annotated[
        str | None,
        typer.Option(
            help="Any breaking changes included with this commit",
        ),
    ] = None,
    type: Annotated[
        CommitTypes,
        typer.Option(
            help="The type of commit this is. Defaults to 'feat', which is short for 'feature'",
        ),
    ] = CommitTypes.FEAT,
    scope: Annotated[
        str | None,
        typer.Option(
            help="The scope of work for this commit. This will typically be a ticket ID, e.g. Jira issue number, or some other work identifier, along with a short name for the internal subcomponent this is for",
        ),
    ] = None,
    time: Annotated[
        str | None,
        typer.Option(
            help="Time tracking details for use with systems like Atlassian Smart Commits",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            help="If True, does not actually make the commit, but instead passes '--dry-run' to git underneath to simulate what the commit would do",
        ),
    ] = False,
    push: Annotated[
        bool,
        typer.Option(
            help="If True, performs a git push automatically after making the commit",
        ),
    ] = True,
):
    gyt_cli_config = GytCliConfig()
    if isinstance(gyt_cli_config.jira, dict):
        gyt_cli_config.jira = JiraConfig(**gyt_cli_config.jira)
    if isinstance(gyt_cli_config.commit, dict):
        gyt_cli_config.commit = CommitConfig(**gyt_cli_config.commit)

    if type is None:
        type_str = (
            gyt_cli_config.commit.default_type
            if gyt_cli_config.commit.default_type
            else CommitTypes.FEAT.value
        )
    else:
        type_str = type.value

    msg_str = message
    if all:
        sub = "-am"
    else:
        sub = "-m"

    msg = type_str
    if scope:
        msg = f"{msg}({scope})"
    else:
        current_branch = git.Repo(search_parent_directories=True).active_branch.name
        jira_pattern = re.compile(r"([A-Z]+\-\d+)")
        found = [m.group(0) for m in jira_pattern.finditer(current_branch)]
        if len(found) > 0:
            msg += "(" + ",".join(found) + ")"

    if gyt_cli_config.jira.include_comment:
        msg += f": #comment {msg_str}"
    else:
        msg += f": {msg_str}"

    if time:
        msg += f" #time {time} {msg_str}"

    cmd = ["git", "commit", sub, msg]

    full_msg_str = msg
    if body:
        cmd.extend(["-m", body])
        full_msg_str += "\n\n" + body
    if breaking_changes:
        brk_chg_str = f"BREAKING CHANGE: {breaking_changes}"
        cmd.extend(["-m", brk_chg_str])
        full_msg_str += "\n\n" + brk_chg_str

    print(
        f"= = = Rendered commit message = = =\n{full_msg_str}\n= = = = = = = = = = = = = = = = = =\n"
    )

    if dry_run:
        cmd.append("--dry-run")

    out = subprocess.run(
        cmd,
        check=False,
        text=True,
    )

    if out.returncode == 0:
        print("Commit successful!")
        if push:
            print("Pushing changes to remote now...")
            print("Running git command: git push\n")
            out = subprocess.run(
                ["git", "push"],
                check=False,
                text=True,
            )

    sys.exit(out.returncode)


if __name__ == "__main__":
    app()
