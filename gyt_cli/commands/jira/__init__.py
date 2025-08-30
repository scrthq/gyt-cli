import typer

from gyt_cli.commands.jira.config import add_project
from gyt_cli.commands.jira.open import open_jira

app = typer.Typer(
    help="Commands to help with Jira issue management in relation to development work in Git.",
)
app.callback(invoke_without_command=True)(open_jira)

app.command()(add_project)

if __name__ == "__main__":
    app()
