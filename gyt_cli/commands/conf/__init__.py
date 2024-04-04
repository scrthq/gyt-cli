from gyt_cli.commands.conf.init import init
from gyt_cli.commands.conf.get import get
from gyt_cli.commands.conf.path import path
from gyt_cli.commands.conf.aliases import add_gyt_aliases

import typer

app = typer.Typer(
    help="Commands to help with core configuration of the Gyt CLI. Configuration specific to subcommands should be managed within those subcommands.",
)
app.command()(init)
app.command()(get)
app.command()(path)
app.command()(add_gyt_aliases)

if __name__ == "__main__":
    app()
