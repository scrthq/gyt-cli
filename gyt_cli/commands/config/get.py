from gyt_cli.constants import APP_CONFIG_PATH


def get():
    with open(APP_CONFIG_PATH, "r") as f:
        print(f.read())
