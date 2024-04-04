from gyt_cli.commands.config.init import init
from gyt_cli.commands.config.get import get
from gyt_cli.commands.config.path import path

import typer

app = typer.Typer(
    help="Commands to help with core configuration of the Gyt CLI. Configuration specific to subcommands should be managed within those subcommands.",
)
app.command()(init)
app.command()(get)
app.command()(path)

if __name__ == "__main__":
    app()
