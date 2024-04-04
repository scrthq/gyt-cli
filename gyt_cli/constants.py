from pathlib import Path
import typer

APP_NAME = "gyt-cli"
APP_CONFIG_DIR: Path = Path(typer.get_app_dir(APP_NAME))
APP_CONFIG_PATH: Path = APP_CONFIG_DIR.joinpath("config.yaml")
