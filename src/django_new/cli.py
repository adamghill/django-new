import importlib.resources
import logging
from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer
from rich.markup import escape
from rich.prompt import Confirm, Prompt
from rich.text import Text
from rich.tree import Tree

from django_new.creators.app import (
    ApiAppCreator,
    AppCreator,
    WebAppCreator,
    WorkerAppCreator,
)
from django_new.creators.project import (
    ClassicProjectCreator,
    MinimalProjectCreator,
    TemplateProjectCreator,
)
from django_new.utils import console, is_running_under_any_uv, stderr

try:
    from django.core.management.base import CommandError
except ImportError as exc:
    # This should never happen because `Django` is a dependency of `django-new`
    raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc

logger = logging.getLogger(__name__)

app = typer.Typer(help="Create a new Django project.")


def version_callback(show_version: Annotated[bool, typer.Option()] = False) -> None:  # noqa: FBT002
    """Show the version and exit.

    Args:
        show_version: Whether to show the version and exit
    """
    if not show_version:
        return

    version_str = ""

    try:
        version_str = version("django-new")
    except ImportError:
        logger.debug("Could not get version from importlib.metadata, so falling back to reading pyproject.toml")

        try:
            from tomlkit import loads as toml_loads  # noqa: PLC0415

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
    name: str | None = typer.Argument(None, help="Project name"),
    folder: str | None = typer.Argument(
        None, help="Optional project folder to create the project in. Defaults to the current directory."
    ),
    project: bool = typer.Option(False, "--project", help="Create a project without an app."),  # noqa: FBT001
    minimal: bool = typer.Option(False, "--minimal", help="Create a minimal project."),  # noqa: FBT001
    app: bool = typer.Option(False, "--app", help="Create a default app."),  # noqa: FBT001
    web: bool = typer.Option(False, "--web", help="Create a website."),  # noqa: FBT001
    api: bool = typer.Option(False, "--api", help="Create an API."),  # noqa: FBT001
    worker: bool = typer.Option(False, "--worker", help="Create a worker."),  # noqa: FBT001
    python_version: str = typer.Option(
        ">=3.10",
        "--python",
        help="Python version requirement (e.g., '>=3.10', '>=3.9,<3.12').",
    ),
    django_version: str = typer.Option(
        ">=5",
        "--django",
        help="Django version requirement (e.g., '>=5', '>=4.2,<5.0').",
    ),
    template: str | None = typer.Option(
        None,
        "--starter",
        "--template",
        "--project-template",
        help="Template to use to create an application. Can be a URL or a local path.",
    ),
    version: Annotated[  # noqa: ARG001
        bool | None,
        typer.Option(
            "--version",
            callback=version_callback,
            help="Show the version.",
            is_eager=True,
        ),
    ] = None,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output for troubleshooting."),  # noqa: FBT001
    extra_verbose: bool = typer.Option(  # noqa: FBT001
        False, "--extra-verbose", "-vv", help="Enable extra verbose output for troubleshooting."
    ),
):
    """Create a new Django project."""

    # Configure logging based on verbose flag
    if verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(levelname)s: %(message)s",
        )
        logger.info("Verbose mode enabled")
    elif extra_verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s: %(message)s",
        )
        logger.debug("Extra verbose mode enabled")
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(message)s",
        )

    # Check for multiple flags at once that don't make sense being used together
    if sum([project, app, api, web, worker, template is not None]) > 1:
        stderr(
            "Cannot specify more than one of --project, --app, --api, --web, --worker, --starter-kit at the same time"
        )

        raise typer.Exit(1)

    console.print("\n[green4]Preparing to create Django magic with django-new ✨[/green4]\n")

    django_new_type = "application"

    if project:
        django_new_type = "project"
    elif app:
        django_new_type = "app"

    # Prompt for name
    if name is None:
        while not name:
            name = Prompt.ask("[yellow]What would you like the application name to be[/yellow]").strip()

            if not name:
                console.print("[red]Application name cannot be empty.[/red]")
            elif not name.replace("-", "").replace("_", "").isalnum():
                console.print(
                    "[red]Application name can only contain letters, numbers, hyphens, and underscores.[/red]"
                )
                name = None
            else:
                if folder is not None:
                    typer.echo()

                break

    # Prompt for folder
    if folder is None:
        default_folder = f"./{name}" if folder_has_files_or_directories(Path(".")) else "."

        folder = Prompt.ask(
            f"[yellow]Where should the new {django_new_type} be created?[/yellow]", default=default_folder
        )
        typer.echo()

    # Handle folder arg
    (folder_path, project_already_existed) = get_folder_path(name, folder)

    # Handle name normalization
    project_name = name
    app_name = get_app_name(name)

    try:
        # Create project
        if not app:
            if project_already_existed:
                logger.debug("Project already exists")

                if minimal:
                    stderr("Project already exists, so cannot make a minimal project")

                    raise typer.Exit(1)
                elif project:
                    stderr("Project already exists, so cannot make a project")

                    raise typer.Exit(1)
                elif template:
                    stderr("Project already exists, so cannot use a template")

                    raise typer.Exit(1)
            elif minimal:
                with console.status("Setting up your minimal project...", spinner="dots"):
                    logger.debug("Project doesn't exist; make minimal")
                    MinimalProjectCreator(name=app_name, folder=folder_path).create(
                        python_version=python_version, django_version=django_version
                    )
            elif template:
                with console.status("Setting up your project with starter kit...", spinner="dots"):
                    logger.debug("Project doesn't exist; make with starter kit")
                    TemplateProjectCreator(name=project_name, folder=folder_path).create(
                        project_template=template, python_version=python_version, django_version=django_version
                    )
            else:
                with console.status("Setting up your project...", spinner="dots"):
                    logger.debug("Project doesn't exist; make classic")
                    ClassicProjectCreator(folder=folder_path).create(
                        display_name=project_name, python_version=python_version, django_version=django_version
                    )

        # Create app
        if not project and not minimal and not template:
            subclassed_app_name = app_name

            if not project_already_existed:
                # Set this to `None` which will use the default app name for each subclass
                subclassed_app_name = None

            with console.status("Setting up your app...", spinner="dots"):
                if api:
                    ApiAppCreator(app_name=subclassed_app_name, folder=folder_path).create()
                elif web:
                    WebAppCreator(app_name=subclassed_app_name, folder=folder_path).create()
                elif worker:
                    WorkerAppCreator(app_name=subclassed_app_name, folder=folder_path).create()
                else:
                    # Always pass in the actual name for default apps
                    AppCreator(app_name=app_name, folder=folder_path).create()
    except CommandError as e:
        cmd_error = str(e)

        stderr(cmd_error)

        raise typer.Exit(1) from e

    # Create and show success message
    typer.echo()
    tree = Tree(
        f":open_file_folder: [link file://{folder_path}]{folder_path}",
        guide_style="",
    )
    walk_directory(folder_path, tree)
    console.print(tree)

    if project_already_existed:
        console.print("\nSuccess! 🚀\n")
    else:
        console.print("\nThe new Django project is ready to go! 🚀")

        run_command = "python manage.py runserver"

        if is_running_under_any_uv():
            run_command = "uv run python manage.py runserver"

        if str(folder_path) != ".":
            console.print("Enter your project directory with [green4]cd [/green4]", end="")

            folder_cd_command = Text(str(folder_path), "green4")
            folder_cd_command.stylize(f"link file://{folder_path}")
            console.print(folder_cd_command)
        else:
            console.print("The new Django project is ready to go! 🚀")

        console.print(f"Run [green4]{run_command}[/green4] to start the development server.")


def walk_directory(directory: Path, tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""

    # Sort dirs first then by filename
    paths = sorted(
        directory.iterdir(),
        key=lambda path: (path.is_file(), path.name.lower()),
    )

    for path in paths:
        # Remove hidden files
        if path.name.startswith("."):
            continue

        if path.is_dir():
            style = "dim" if path.name.startswith("__") else ""

            branch = tree.add(
                f":open_file_folder: [link file://{path}]{escape(path.name)}",
                style=style,
                guide_style=style,
            )
            walk_directory(path, branch)
        else:
            text_filename = Text(path.name, "blue")
            text_filename.stylize(f"link file://{path}")

            tree.add(text_filename)


def folder_has_files_or_directories(path: Path) -> bool:
    """Check if a folder has any files or directories (excluding hidden ones)."""

    if not path.exists() or not path.is_dir():
        return False

    try:
        for item in path.iterdir():
            if not item.name.startswith("."):
                return True

        return False
    except (OSError, PermissionError):
        return False


def get_folder_path(name: str, folder: str) -> tuple[Path, bool]:
    """Get the resolved folder path."""

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

    has_files = folder_has_files_or_directories(folder_path)

    if has_files and not project_already_existed:
        logger.debug("Target directory has files/directories")

        if folder == ".":
            response = Confirm.ask(
                "[yellow]Hmm, the current directory is not empty. Should a new directory be created here?[/yellow]",
                default=True,
            )
        else:
            response = Confirm.ask(
                "[yellow]Hmm, the target directory is not empty. Should a new directory be created in it?[/yellow]",
                default=True,
            )

        folder_name = name

        if response:
            folder_name = Prompt.ask("[yellow]What should be the name of the new directory?[/yellow]", default=name)
        else:
            response = Confirm.ask(
                f"[yellow]This will create files in '{folder_path}'. "
                "Are you sure you don't want to create a new directory?[/yellow]",
                default=True,
            )

            if response:
                return (folder_path, project_already_existed)
            else:
                folder_name = Prompt.ask(
                    "[yellow]Oh ok! What should be the name of the new directory?[/yellow]", default=name
                )

        folder_path = folder_path / folder_name
        folder_path.mkdir(exist_ok=True)
        project_already_existed = False
        typer.echo()

    return (folder_path, project_already_existed)


def get_app_name(name: str) -> str:
    """Get the app name, handling dashes if present."""

    if "-" in name:
        potential_app_name = name.replace("-", "_")

        user_input = Confirm.ask(
            f"[yellow]Uh oh, dashes are not allowed in Python modules. 😞 Would you like to use '{potential_app_name}' "
            "for the app folder instead?[/yellow]",
            default=True,
        )

        if not user_input:
            console.print("[red]Please try again with a name that doesn't contain dashes.[/red]")

            raise typer.Exit(0)

        typer.echo()

        return potential_app_name

    return name


def main():
    # This is the entry point for the CLI
    app()


# Register the command
app.command()(create_project)

if __name__ == "__main__":
    app()
