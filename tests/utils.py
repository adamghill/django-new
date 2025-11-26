import logging
import os
import sys
from pathlib import Path

from django_new.cli import main

logger = logging.getLogger(__name__)


def call_main(monkeypatch, path: Path, name: str, *flags):
    args = ["django-new", name, str(path), *flags]
    monkeypatch.setattr(sys, "argv", args)
    main()


def print_directory_structure(startpath):
    """Print the directory structure starting from startpath."""

    # Recurse into subdirectories
    if os.path.isdir(startpath):
        try:
            items = sorted(os.listdir(startpath))

            for i, item in enumerate(items):
                path = os.path.join(startpath, item)
                is_last = i == len(items) - 1
                print_directory_structure(path)
        except (PermissionError, OSError):
            pass  # Skip directories we can't access
    else:
        logger.debug(startpath)
