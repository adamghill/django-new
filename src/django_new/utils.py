import logging
from io import StringIO

from rich.console import Console

try:
    from django.core.management import call_command as django_call_command
except ImportError as exc:
    # This should never happen because `Django` is a dependency of `django-new`
    raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc


logger = logging.getLogger(__name__)

console = Console()
error_console = Console(stderr=True)


def stdout(message: str):
    console.print(message)


def stderr(message: str):
    error_console.print(message, style="red")


def call_command(*args) -> tuple[str, str]:
    """Call a Django management command and capture its output.

    Args:
        *args: Command name and arguments to pass to the command.

    Returns:
        A tuple of (stdout, stderr).
    """

    # Redirect stdout and stderr to capture the output
    out = StringIO()
    err = StringIO()

    logger.debug(f"Call command with args: {args}")

    django_call_command(*args, stdout=out, stderr=err)

    stdout_str = out.getvalue()
    stderr_str = err.getvalue()

    return (stdout_str, stderr_str)
