import logging
import os

logger = logging.getLogger(__name__)


def print_directory_structure(path):
    """Print the directory structure starting from path."""

    # Recurse into subdirectories
    if os.path.isdir(path):
        logger.debug(path)

        try:
            items = sorted(os.listdir(path))

            for _, item in enumerate(items):
                path = os.path.join(path, item)
                print_directory_structure(path)
        except (PermissionError, OSError):
            pass  # Skip directories we can't access
    else:
        logger.debug(path)
