from pathlib import Path
import yaml


CONFIG_FILE = Path("config/settings.yaml")


def load_config():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with open(CONFIG_FILE, "r") as file:
        config = yaml.safe_load(file)

    return config