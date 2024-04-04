from gyt_cli.commands.config.init import init
from gyt_cli.commands.config.get import get
from gyt_cli.commands.config.path import path

import typer

app = typer.Typer()
app.command()(init)
app.command()(get)
app.command()(path)

if __name__ == "__main__":
    app()
