from typer.testing import CliRunner

from gyt_cli.cli import app
from gyt_cli import __version__

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
