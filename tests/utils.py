import logging
import os
import sys
from pathlib import Path

from django_new.cli import main

logger = logging.getLogger(__name__)


def call_main(monkeypatch, path: Path, name: str, *flags):
    args = ["django-new", name, str(path), *flags]
    monkeypatch.setattr(sys, "argv", args)

    try:
        main()
    except SystemExit as e:
        if e.code != 0:
            raise


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
