import yaml
import os
from loguru import logger
from pathlib import Path
from typing import Any


def load_yaml_config(config_path: Path = None) -> dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dictionary containing configuration values
    """
    if not config_path:
        return {}

    try:
        config_file = Path(config_path).expanduser().resolve() or None
        if not config_file or not config_file.exists():
            logger.warning(f"Configuration file not found: {config_file}")
            return {}
        if not config_file.is_file():
            logger.error(f"Provided configuration path is not a file: {config_file}")
            return {}

        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

        # Convert string paths to Path objects and expand user paths
        path_keys = ['export_dir', 'nc_photos_dir', 'log_file']
        for key in path_keys:
            if key in config and config[key]:
                config[key] = str(Path(config[key]).expanduser().resolve())

        logger.info(f"Loaded configuration from {config_file}")
        return config

    except Exception as e:
        logger.error(f"Error loading configuration file {config_path}: {e}")
        return {}