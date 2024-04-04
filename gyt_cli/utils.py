import yaml

from gyt_cli.config.model import GytCliConfig
from gyt_cli.constants import APP_CONFIG_PATH

def load_config() -> GytCliConfig:
    with open(APP_CONFIG_PATH, "r") as f:
        config_dict = yaml.safe_load(f)
    return GytCliConfig.model_validate(config_dict)
