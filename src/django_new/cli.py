import argparse
import logging
import sys
from pathlib import Path

from django_new.creators.app import ApiAppCreator, AppCreator, WebAppCreator, WorkerAppCreator
from django_new.creators.project import ClassicProjectCreator, MinimalProjectCreator
from django_new.utils import is_running_under_any_uv, print_error, print_success

try:
    from django.core.management.base import CommandError
except ImportError as exc:
    # This should never happen because `Django` is a dependency of `django-new`
    raise ImportError("Couldn't import Django. Are you sure it's installed?") from exc

logger = logging.getLogger(__name__)


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
                MinimalProjectCreator(name=args.name, folder=args.folder).create()
            else:
                logger.debug("Project doesn't exist; make classic")
                ClassicProjectCreator(folder=args.folder).create(display_name=args.name)

        app_name = get_app_name(args)

        if not args.project and not args.minimal:
            if args.api:
                ApiAppCreator(app_name=app_name, folder=args.folder).create()
            elif args.web:
                WebAppCreator(app_name=app_name, folder=args.folder).create()
            elif args.worker:
                WorkerAppCreator(app_name=app_name, folder=args.folder).create()
            else:
                AppCreator(app_name=app_name, folder=args.folder).create()
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
