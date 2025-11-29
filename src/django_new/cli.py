import importlib.resources
import logging
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from django_new.creators.app import ApiAppCreator, AppCreator, WebAppCreator, WorkerAppCreator
from django_new.creators.project import ClassicProjectCreator, MinimalProjectCreator
from django_new.utils import console, is_running_under_any_uv, stderr, stdout

try:
    from tomllib import loads as toml_loads
except ImportError:
    from tomli import loads as toml_loads

try:
    from django.core.management.base import CommandError
except ImportError as exc:
    # This should never happen because `Django` is a dependency of `django-new`
    raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc

logger = logging.getLogger(__name__)

app = typer.Typer(help="Create a new Django project.")


def version_callback(show_version: bool) -> None:  # noqa: FBT001
    """Show the version and exit."""

    if not show_version:
        return

    version_str = ""

    try:
        version_str = version("django-new")
    except ImportError:
        logger.debug("Could not get version from importlib.metadata, so falling back to reading pyproject.toml")

        try:
            resource = importlib.resources.files("django_new").parent.parent / "pyproject.toml"
            version_str = toml_loads(resource.read_text()).get("project", {}).get("version")
        except Exception as e:
            logger.error("Failed to read version from pyproject.toml", exc_info=e)

    if version_str:
        typer.echo(f"django-new v{version_str}")
    else:
        typer.echo("django-new (version unknown)")

    raise typer.Exit()


def create_project(
    name: str = typer.Argument(..., help="Project name"),
    folder: str = typer.Argument(
        ".", help="Optional project folder to create the project in. Defaults to the current directory."
    ),
    project: bool = typer.Option(False, "--project", "-p", help="Create a project without an app."),  # noqa: FBT001
    minimal: bool = typer.Option(False, "--minimal", "-m", help="Create a minimal project."),  # noqa: FBT001
    app: bool = typer.Option(False, "--app", help="Create a default app."),  # noqa: FBT001
    web: bool = typer.Option(False, "--web", help="Create a website."),  # noqa: FBT001
    api: bool = typer.Option(False, "--api", help="Create an API."),  # noqa: FBT001
    worker: bool = typer.Option(False, "--worker", help="Create a worker."),  # noqa: FBT001
    version: Annotated[  # noqa: ARG001
        bool | None, typer.Option("--version", callback=version_callback, help="Show the version.")
    ] = None,
):
    """
    Create a new Django project.
    """

    # Check for multiple flags at once that don't make sense being used together
    if sum([project, app, api, web, worker]) > 1:
        stderr("Cannot specify more than one of --project, --app, --api, --web, --worker at the same time")

        raise typer.Exit(1)

    # Handle folder arg
    project_already_existed = False
    folder_path = Path(folder).resolve()

    if str(folder_path) != ".":
        logger.debug(f"Create target directory, {folder_path}, if it doesn't exist")

        if folder_path.exists():
            project_already_existed = folder_path.is_dir() and (folder_path / "manage.py").exists()
        else:
            logger.debug(f"Create project dir {folder_path}")
            folder_path.mkdir(parents=True, exist_ok=True)
    else:
        logger.debug("Target directory is current directory")
        folder_path = Path.cwd()

    try:
        if not app:
            if project_already_existed:
                logger.debug("Project already exists")

                if minimal:
                    stderr("Project already exists, so cannot make a minimal project")

                    raise typer.Exit(1)
                elif project:
                    stderr("Project already exists, so cannot make a project")

                    raise typer.Exit(1)
            elif minimal:
                with console.status("Setting up your minimal project...", spinner="dots"):
                    logger.debug("Project doesn't exist; make minimal")
                    MinimalProjectCreator(name=name, folder=folder_path).create()
            else:
                with console.status("Setting up your project...", spinner="dots"):
                    logger.debug("Project doesn't exist; make classic")
                    ClassicProjectCreator(folder=folder_path).create(display_name=name)

        if not project and not minimal:
            app_name = name

            if not project_already_existed:
                # Set this to `None` which will use the default app name for each subclass
                app_name = None

            with console.status("Setting up your app...", spinner="dots"):
                if api:
                    ApiAppCreator(app_name=app_name, folder=folder_path).create()
                elif web:
                    WebAppCreator(app_name=app_name, folder=folder_path).create()
                elif worker:
                    WorkerAppCreator(app_name=app_name, folder=folder_path).create()
                else:
                    # Always pass in the actual name for default apps
                    AppCreator(app_name=name, folder=folder_path).create()
    except CommandError as e:
        stderr(str(e))

        raise typer.Exit(1) from e

    if project_already_existed:
        stdout("\nSuccess! 🚀\n")
    else:
        run_command = "python manage.py runserver"
        cd_command = ""

        if is_running_under_any_uv():
            run_command = "uv run python manage.py runserver"

        if str(folder_path) != ".":
            cd_command = f"Enter your project directory with [green4]cd {folder_path}[/green4].\n   "

        stdout(f"""
   The new Django project is ready to go! 🚀
   {cd_command}Run [green4]{run_command}[/green4] to start the development server.
""")


def main():
    # This is the entry point for the CLI
    app()


# Register the command
app.command()(create_project)


if __name__ == "__main__":
    app()
