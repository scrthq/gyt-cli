from gyt_cli.config.model import GytCliConfig
from gyt_cli.constants import APP_CONFIG_PATH


def init():
    APP_CONFIG_PATH.parent.mkdir(exist_ok=True, parents=True)
    if not APP_CONFIG_PATH.exists():
        gyt_config = GytCliConfig()
        gyt_config.save()
        print(f"Configuration initialized @ {APP_CONFIG_PATH}")
    else:
        print(f"Configuration already exists @ {APP_CONFIG_PATH}")
