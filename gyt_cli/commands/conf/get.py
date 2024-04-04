from gyt_cli.constants import APP_CONFIG_PATH
from rich.console import Console
from rich.syntax import Syntax,SyntaxTheme


def get():
    console = Console()
    with open(APP_CONFIG_PATH, "r") as f:
        syntax = Syntax(f.read(), 'yaml', theme="ansi_dark")
        console.print(syntax)
