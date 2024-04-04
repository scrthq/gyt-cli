from gyt_cli.commands.ci import app as ci
from gyt_cli.commands.cleant import app as cleant
from gyt_cli.commands.commit import app as commit
from gyt_cli.commands.config import app as config
from gyt_cli.commands.fresh import app as fresh
from gyt_cli.commands.jira import app as jira
from gyt_cli.commands.repo import app as repo

import typer

app = typer.Typer(
    help="~~Pretty~~ Gitty Young Thang CLI",
)

app.add_typer(ci, name="ci")
app.add_typer(cleant, name="cleant")
app.add_typer(commit, name="commit")
app.add_typer(config, name="config")
app.add_typer(fresh, name="fresh")
app.add_typer(jira, name="jira")
app.add_typer(repo, name="repo")

if __name__ == "__main__":
    app()
