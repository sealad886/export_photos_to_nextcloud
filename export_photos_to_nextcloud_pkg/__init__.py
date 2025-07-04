"""
Export Photos to Nextcloud

A modern Python tool for exporting photos from Apple Photos.app and syncing them
to Nextcloud with beautiful progress tracking and robust logging.
"""

__version__ = "1.0.0"
__description__ = "Export photos from Apple Photos.app to Nextcloud with a `{year}/{month}` folder structure for more easily sideloading a large library to Nextcloud AIO during a user's initial setup."

# Import main components
from .main import main, Config, PhotoExporter

__all__ = ["main", "Config", "PhotoExporter", "__version__"]
