from enum import Enum
import subprocess
from typing import Literal
from gyt_cli.utils import list_subcommands

class AliasScope(Enum):
    GLOBAL = "global"
    LOCAL = "local"


def add_gyt_aliases(scope: AliasScope = "global"):
    subcommands = list_subcommands()
    for subcommand in subcommands:
        print(f"Adding {scope.value} git alias for {subcommand}: !gyt {subcommand}")
        git_cmd = [
            "git",
            "config",
        ]
        if scope == AliasScope.GLOBAL:
            git_cmd.append("--global")
        git_cmd += [
            f"alias.{subcommand}",
            f"!gyt {subcommand}",
        ]
        print(f"Running: {' '.join(git_cmd)}")
        subprocess.run(git_cmd, check=True, text=True)
