# import subprocess
# import git
# import re
# from typing_extensions import Annotated
import typer

app = typer.Typer(
    help="Opens the CI/CD pipeline in the browser. Currently only supports GitHub Actions."
)

if __name__ == "__main__":
    app()
