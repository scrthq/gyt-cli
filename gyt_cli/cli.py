from typing_extensions import Annotated
from gyt_cli import __version__

from gyt_cli.commands.ci import app as ci
from gyt_cli.commands.cleant import app as cleant
from gyt_cli.commands.camp import app as camp
from gyt_cli.commands.conf import app as conf
from gyt_cli.commands.fresh import app as fresh
from gyt_cli.commands.jira import app as jira
from gyt_cli.commands.repo import app as repo

import typer

app = typer.Typer(
    help="Gitty Young Thang CLI",
)


@app.callback(
    no_args_is_help=True,
    invoke_without_command=True,
)
def gyt_main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version",
        ),
    ] = False,
):
    if version:
        typer.echo(f"Gitty Young Thang CLI version: {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo("No command specified")
        raise typer.Exit()
    return None


app.add_typer(ci, name="ci")
app.add_typer(cleant, name="cleant")
app.add_typer(camp, name="camp")
app.add_typer(conf, name="conf")
app.add_typer(fresh, name="fresh")
app.add_typer(jira, name="jira")
app.add_typer(repo, name="repo")

if __name__ == "__main__":
    app()
