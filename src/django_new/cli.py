import os
import sys
from pathlib import Path

from django_new.formatters.add import add_to_list


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc

    # Remove the command name from the arguments
    if len(sys.argv) > 1 and sys.argv[1] == "django-new":
        sys.argv.pop(1)

    execute_from_command_line([sys.argv[0], "startproject", "config", "."])

    add_to_list(Path("config/settings.py"), "INSTALLED_APPS", '"config.apps.ConfigApp"')
