# import subprocess
# import git
# import re
# from typing_extensions import Annotated
import typer

app = typer.Typer(
    help="Starts a fresh feature branch and syncs with the remote.",
)

if __name__ == "__main__":
    app()