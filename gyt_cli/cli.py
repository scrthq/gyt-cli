from typing_extensions import Annotated
from gyt_cli import __version__

from gyt_cli.commands.ci import app as ci
from gyt_cli.commands.cleant import app as cleant
from gyt_cli.commands.camp import app as camp
from gyt_cli.commands.conf import app as conf
from gyt_cli.commands.fresh import app as fresh
from gyt_cli.commands.jira import app as jira
from gyt_cli.commands.repo import app as repo
from gyt_cli.commands.branches import app as branches
from gyt_cli.commands.fixup import app as fixup
from gyt_cli.commands.pr import app as pr
from gyt_cli.commands.rename import app as rename
from gyt_cli.commands.squash import app as squash
from gyt_cli.commands.sync import app as sync
from gyt_cli.commands.tree import app as tree
from gyt_cli.commands.undo import app as undo
from gyt_cli.commands.unwip import app as unwip
from gyt_cli.commands.wip import app as wip

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
app.add_typer(branches, name="branches")
app.add_typer(fixup, name="fixup")
app.add_typer(pr, name="pr")
app.add_typer(rename, name="rename")
app.add_typer(squash, name="squash")
app.add_typer(sync, name="sync")
app.add_typer(tree, name="tree")
app.add_typer(undo, name="undo")
app.add_typer(unwip, name="unwip")
app.add_typer(wip, name="wip")

if __name__ == "__main__":
    app()
