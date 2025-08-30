from gyt_cli.config.model import GytCliConfig
from rich.console import Console
from rich.syntax import Syntax


def get(return_only: bool = False):
    config = GytCliConfig()
    if return_only:
        return config.model_dump()
    console = Console()
    with open(config.config_path, "r") as f:
        syntax = Syntax(f.read(), "yaml", theme="ansi_dark")
        console.print(syntax)
