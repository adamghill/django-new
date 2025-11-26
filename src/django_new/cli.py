import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from shutil import rmtree
from typing import Any

from django.template import Context, Engine

from django_new.formatters.adder import add_to_list
from django_new.parser import get_class_name

try:
    from django.core.management import call_command as django_call_command
    from django.core.management.base import CommandError
except ImportError as exc:
    # This should never happen because `Django` is a dependency of `django-new`
    raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc

logger = logging.getLogger(__name__)


CLASSIC_CONFIGURATION_PATH_NAME = "config"


@dataclass(frozen=True)
class TemplateFile:
    path: Path
    context: dict[str, Any] = field(default_factory=dict)


def main():
    # TODO: Do I need this?
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django.conf.global_settings")

    args = get_args()

    try:
        if not args.app:
            if args.project_already_existed:
                logger.debug("Project already exists")

                if args.minimal:
                    print_error("Project already exists, so cannot make a minimal project")

                    sys.exit(1)
                elif args.project:
                    print_error("Project already exists, so cannot make a project")

                    sys.exit(1)
            elif args.minimal:
                logger.debug("Project doesn't exist; make minimal")
                create_minimal(args)
            else:
                logger.debug("Project doesn't exist; make classic")
                create_project(name=CLASSIC_CONFIGURATION_PATH_NAME, display_name=args.name, folder=args.folder)

        app_name = get_app_name(args)

        if not args.project and not args.minimal:
            if args.api:
                create_app(name=app_name, folder=args.folder)
            elif args.web:
                create_app(name=app_name, folder=args.folder)
            elif args.worker:
                create_app(name=app_name, folder=args.folder)

                # Create tasks.py
                create_file(template_file=TemplateFile(path=args.folder / app_name / "tasks.py"))

                # Remove views.py and urls.py
                (args.folder / app_name / "views.py").unlink(missing_ok=True)
                (args.folder / app_name / "urls.py").unlink(missing_ok=True)
            else:
                create_app(name=args.name, folder=args.folder)
    except CommandError as e:
        print_error(e)
        sys.exit(1)

    if args.project_already_existed:
        print_success("\nSuccess! 🚀\n")
    elif is_running_under_any_uv():
        print_success("\nSuccess! Run 'uv run python manage.py runserver' to start the development server. 🚀\n")
    else:
        print_success("\nSuccess! Run 'python manage.py runserver' to start the development server. 🚀\n")


def get_args():
    parser = argparse.ArgumentParser(description="Creates a new Django project or app")

    parser.add_argument(
        "name",
        help="Required project name.",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Optional project folder to create the project in. Default: current directory.",
    )
    parser.add_argument(
        "--project",
        action="store_true",
        default=False,
        help="Create a default project without an app.",
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        default=False,
        help="Create a minimal project structure.",
    )
    parser.add_argument(
        "--app",
        action="store_true",
        default=False,
        help="Create an app structure with a project.",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        default=False,
        help="Create a web project structure.",
    )
    parser.add_argument(
        "--api",
        action="store_true",
        default=False,
        help="Create an API project structure.",
    )
    parser.add_argument(
        "--worker",
        action="store_true",
        default=False,
        help="Create a worker project structure.",
    )

    args = parser.parse_args()

    # Check for multiple flags at once that don't make sense being used together
    if sum([args.project, args.app, args.api, args.web, args.worker]) > 1:
        print_error("Cannot specify more than one of --project, --app, --api, --web, --worker at the same time")
        sys.exit(1)

    # Handle folder arg
    if args.folder != ".":
        logger.debug(f"Create target directory, {args.folder}, if it doesn't exist")
        project_dir = Path(args.folder).resolve()

        args.project_already_existed = False

        if project_dir.exists():
            args.project_already_existed = project_dir.is_dir() and (project_dir / "manage.py").exists()
        else:
            logger.debug(f"Create project dir {project_dir}")

        project_dir.mkdir(parents=True, exist_ok=True)
    else:
        logger.debug("Target directory is current directory")

    args.folder = Path(args.folder).resolve()

    return args


def get_app_name(args):
    app_name = args.name

    if args.project_already_existed:
        logger.debug("Project already exists, so use the specified app name")
    elif args.app:
        logger.debug("Use app name explicitly")
    elif args.api:
        logger.debug("Use 'api' as app name")
        app_name = "api"
    elif args.web:
        logger.debug("Use 'web' as app name")
        app_name = "web"
    elif args.worker:
        logger.debug("Use 'worker' as app name")
        app_name = "worker"
    else:
        logger.debug(f"Use '{args.name}' as app name")

    return app_name


def is_running_under_any_uv():
    uv_vars = [
        "UV_PROJECT_ENVIRONMENT",
        "UV_INTERNAL__PARENT_INTERPRETER",
        "VIRTUAL_ENV",  # uv also sets this when creating venvs
    ]

    return any(os.getenv(var) for var in uv_vars)


def add_app_to_installed_apps(name: str, apps_path: Path, settings_path: Path):
    logger.debug(f"Add {name} to INSTALLED_APPS")

    if apps_path.exists():
        app_config_name = get_class_name(path=apps_path, base_class_name="AppConfig")

        if app_config_name:
            fully_qualified_app_config_name = f'"{name}.apps.{app_config_name}"'

            add_to_list(
                path=settings_path,
                target_variable_name="INSTALLED_APPS",
                new_list_element=fully_qualified_app_config_name,
            )
            print_success(f"✅ {fully_qualified_app_config_name} added to INSTALLED_APPS")
        else:
            logger.error("app_config_name could not be determined")
    else:
        logger.error("apps.py doesn't exist")


def create_minimal(args):
    create_project(name=args.name, folder=args.folder)
    create_app(name=args.name, folder=args.folder / args.name, is_quiet=True)

    logger.debug("Move app to project folder")
    for item in (args.folder / args.name / args.name).iterdir():
        target = (args.folder / args.name) / item.name

        if not target.exists():
            logger.debug(f"Move {item} -> {target}")
            item.replace(target)

    logger.debug("Remove temporary app directory")
    rmtree(args.folder / args.name / args.name, ignore_errors=True)
    logger.debug("Finished cleaning up temporary app directory")


def create_classic(args):
    # TODO: Is this needed?
    (args.folder / args.name).mkdir(parents=True, exist_ok=True)

    create_project(name=CLASSIC_CONFIGURATION_PATH_NAME, display_name=args.name, folder=args.folder)
    create_app(name=args.name, folder=args.folder)


def create_file(template_file: TemplateFile, resource_name: str = "django_new", resource_path: str = "templates"):
    """Create file based on a DTL template in a specified resource."""

    logger.debug(f"Create file, {template_file.path}, if it doesn't exist")
    engine = Engine(debug=False, autoescape=False)

    if template_file.path.exists():
        logger.debug(f"Do not create template file, {template_file.path}, because it already exists")
    else:
        template_name = template_file.path.name + "-tpl"
        logger.debug(f"Template name: {template_name}")

        template_path = resources.files(resource_name) / resource_path / template_name
        template_content = template_path.read_text(encoding="utf-8")
        logger.debug("Read template content")

        template = engine.from_string(template_content)
        rendered_content = template.render(Context(template_file.context or {}))
        logger.debug(f"Render template content with context {template_file.context}")

        template_file.path.write_text(rendered_content)
        logger.debug(f"Created template file, {template_file.path}")


def create_project(name: str, folder: Path, display_name: str | None = None):
    """Create a new Django project."""

    call_command("startproject", name, folder)
    print_success("✅ Project created")

    # Create additional files needed for a new Django project that are not included with `startproject`
    name = display_name or name

    created_files = []
    template_files = (
        TemplateFile(folder / "pyproject.toml", {"name": name}),
        TemplateFile(folder / "README.md", {"name": name}),
        TemplateFile(folder / ".gitignore"),
        TemplateFile(folder / ".env"),
    )

    for template_file in template_files:
        try:
            create_file(template_file=template_file)
            created_files.append(template_file.path.name)
        except Exception as e:
            print_error(str(e))
            continue

    if created_files:
        print_success(f"✅ {', '.join(created_files)} files created")


def create_app(name: str, folder: Path, is_quiet: bool = False):
    """Create a new Django app."""

    logger.debug(f"Start creating app, {name}")

    logger.debug(f"Create app directory, {folder / name}, if it doesn't exist")
    (folder / name).mkdir(parents=True, exist_ok=True)

    call_command("startapp", name, folder / name)
    (folder / name / "urls.py").write_text("# urls.py")

    (folder / name / "tests.py").unlink(missing_ok=True)

    if not is_quiet:
        print_success(f"✅ `{name}` app created")

    apps_path = folder / name / "apps.py"
    settings_path = folder / "settings.py"

    if not settings_path.exists():
        settings_path = folder / CLASSIC_CONFIGURATION_PATH_NAME / "settings.py"

    if settings_path.exists():
        add_app_to_installed_apps(name=name, apps_path=apps_path, settings_path=settings_path)


def call_command(*args):
    logger.debug(f"Call command with args: {args}")
    django_call_command(*args)


def print_error(s: Any) -> None:
    print(f"\033[91m{s}\033[0m")


def print_success(s: Any) -> None:
    print(f"\033[92m{s}\033[0m")
