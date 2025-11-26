import logging
import os
from typing import Any

try:
    from django.core.management import call_command as django_call_command
except ImportError as exc:
    # This should never happen because `Django` is a dependency of `django-new`
    raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc


logger = logging.getLogger(__name__)


def print_error(s: Any) -> None:
    print(f"\033[91m{s}\033[0m")


def print_success(s: Any) -> None:
    print(f"\033[92m{s}\033[0m")


def call_command(*args):
    logger.debug(f"Call command with args: {args}")
    django_call_command(*args)


def is_running_under_any_uv():
    uv_vars = [
        "UV_PROJECT_ENVIRONMENT",
        "UV_INTERNAL__PARENT_INTERPRETER",
        "VIRTUAL_ENV",  # uv also sets this when creating venvs
    ]

    return any(os.getenv(var) for var in uv_vars)
