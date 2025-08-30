import yaml
from pkgutil import iter_modules

import gyt_cli.commands

from gyt_cli.config.model import GytCliConfig
from gyt_cli.constants import APP_CONFIG_PATH


def load_config() -> GytCliConfig:
    with open(APP_CONFIG_PATH, "r") as f:
        config_dict = yaml.safe_load(f)
    return GytCliConfig.model_validate(config_dict)


def list_subcommands() -> list[str]:
    result = []
    for submodule in iter_modules(gyt_cli.commands.__path__):
        result.append(submodule.name)
    return result
