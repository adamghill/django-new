"""Utility for configuring Whitenoise."""

from pathlib import Path
import shlex
import subprocess


def configure_whitenoise(folder_path):
    """Configure Whitenoise.

    Add to requirements, modify MIDDLEWARE.
    """
    # Add whitenoise as a requirement.
    cmd = "uv add whitenoise"
    cmd_parts = shlex.split(cmd)
    subprocess.run(cmd_parts, cwd=folder_path)

    # Add Whitenoise to middleware.
    path_settings = folder_path / "config" / "settings.py"
    settings_text = path_settings.read_text()

    security_mw = "'django.middleware.security.SecurityMiddleware',"
    whitenoise_mw = "'whitenoise.middleware.WhiteNoiseMiddleware',"

    settings_text = settings_text.replace(security_mw, f"{security_mw}\n    {whitenoise_mw}")
    path_settings.write_text(settings_text)

    # Needs some more configuration.