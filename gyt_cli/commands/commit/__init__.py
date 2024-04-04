# import subprocess
# import git
# import re
# from typing_extensions import Annotated
import typer

app = typer.Typer()

#!/usr/bin/env python
"""
## Installation

1. Download this file
2. Remove the .py extension, renaming the file to 'git-camp'
3. Make the file executable: `chmod +x git-camp`
4. Place the file somewhere in PATH so it's accessible from Git
5. Use with Git in place of `git commit`, e.g.

```sh
git camp -am 'added button' \
    --body 'Button enables developers to toggle feature flags within the admin panel' \
    --breaking-changes 'Removes buttonless workflow' \
    --type feat \
    --scope admin
```

Output:

```sh
= = = Rendered commit message = = =
feat(admin): added button

Button enables developers to toggle feature flags within the admin panel

BREAKING CHANGE: Removes buttonless workflow
= = = = = = = = = = = = = = = = = =

The following files have been added, modified, moved, or removed:
********************************************************************

A       button.js


********************************************************************
[main 6b9ade9] feat(admin): added button
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 button.js
Commit successful!
```

## Getting Help

$ git camp -h
usage: git camp [-h] [-m MESSAGE] [-am ALL_WITH_MESSAGE] [--body BODY] [--breaking-changes BREAKING_CHANGES] [--type {feat,fix,docs,style,refactor,test,chore,ci}]
                  [--scope SCOPE] [--dry-run] [--push]

Git Conventional Commit helper script

options:
  -h, --help            show this help message and exit
  -m MESSAGE, --message MESSAGE
                        Commit message subject
  -am ALL_WITH_MESSAGE, --all-with-message ALL_WITH_MESSAGE
                        Commit message with --all included
  --body BODY           Commit message body and additional notes
  --breaking-changes BREAKING_CHANGES
                        Any breaking changes that this commit introduces
  --type {feat,fix,docs,style,refactor,test,chore,ci}
                        Commit type
  --scope SCOPE         Scope of the commit
  --dry-run             Do not actually commit, instead passing --dry-run to git commit
  --no-push             If true, does not perform a git push after a successful commit
"""

import enum
import subprocess
import sys
import re
from typing_extensions import Annotated

try:
    import git
except ModuleNotFoundError:
    subprocess.run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "gitpython"
    ])
    import git

try:
    import typer
except ModuleNotFoundError:
    subprocess.run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "typer",
        "rich",
        "shellingham",
    ])
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
        str,
        typer.Option(
            help="Commit message body",
        ),
    ] = None,
    breaking_changes: Annotated[
        str,
        typer.Option(
            help="Any breaking changes included with this commit",
        ),
    ] = None,
    commit_type: Annotated[
        CommitTypes,
        typer.Option(
            help="The type of commit this is. Defaults to 'feat', which is short for 'feature'",
        ),
    ] = CommitTypes.FEAT.value,
    scope: Annotated[
        str,
        typer.Option(
            help="The scope of work for this commit. This will typically be a ticket ID, e.g. Jira issue number, or some other work identifier, along with a short name for the internal subcomponent this is for",
        ),
    ] = None,
    time: Annotated[
        str,
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
    msg_str = message
    if all:
        sub = "-am"
    else:
        sub = "-m"

    msg = commit_type
    if scope:
        msg += "(" + scope + ")"
    else:
        current_branch = git.Repo(search_parent_directories=True).active_branch.name
        jira_pattern = re.compile(r"([A-Z]+\-\d+)")
        found = [m.group(0) for m in jira_pattern.finditer(current_branch)]
        if len(found) > 0:
            msg += "(" + ",".join(found) + ")"

    if time:
        msg += f": #comment {msg_str}"
        msg += f" #time {time} {msg_str}"
    else:
        msg += f": #comment {msg_str}"

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