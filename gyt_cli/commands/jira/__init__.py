import subprocess
import git
import re
from typing_extensions import Annotated
import typer

from gyt_cli.commands.jira.config import add_project
from gyt_cli.commands.jira.open import open_jira

app = typer.Typer(
    help="JIRA issue helpers",
)
app.callback(invoke_without_command=True)(open_jira)

app.command()(add_project)

if __name__ == "__main__":
    app()
