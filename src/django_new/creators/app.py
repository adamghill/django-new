import logging
from pathlib import Path

from django_new.parser import get_class_name
from django_new.templater.django_template import TemplateFile, create_file
from django_new.transformer import Transformation
from django_new.transformer.operations.python import AppendToList
from django_new.utils import call_command, stdout

logger = logging.getLogger(__name__)


CLASSIC_CONFIGURATION_PATH_NAME = "config"


class AppCreator:
    def __init__(self, app_name: str | None, folder: Path):
        self.app_name = app_name

        if self.app_name is None:
            self.app_name = self.default_app_name

        if not self.app_name:
            raise ValueError("App name is unknown")

        self.folder = folder

    def create(self) -> None:
        """Create a new Django app."""

        logger.debug(f"Start creating app, {self.app_name}")

        logger.debug(f"Create app directory, {self.folder / self.app_name}, if it doesn't exist")
        (self.folder / self.app_name).mkdir(parents=True, exist_ok=True)

        call_command("startapp", self.app_name, self.folder / self.app_name)

        # Remove tests.py in lieu of a root directory named tests
        (self.folder / self.app_name / "tests.py").unlink(missing_ok=True)

        # Create tests directory with __init__.py
        tests_dir = self.folder / "tests" / self.app_name
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "__init__.py").touch(exist_ok=True)
        logger.debug(f"Created tests directory at {tests_dir}")

        settings_path = self.folder / "settings.py"

        # If settings cannot be found, look in "config" folder
        if not settings_path.exists():
            settings_path = self.folder / CLASSIC_CONFIGURATION_PATH_NAME / "settings.py"

        if settings_path.exists():
            apps_path = self.folder / self.app_name / "apps.py"

            self.add_app_to_installed_apps(name=self.app_name, apps_path=apps_path, settings_path=settings_path)

    def add_app_to_installed_apps(self, name: str, apps_path: Path, settings_path: Path):
        logger.debug(f"Add {name} to INSTALLED_APPS")

        if apps_path.exists():
            app_config_name = get_class_name(path=apps_path, base_class_name="AppConfig")

            if app_config_name:
                fully_qualified_app_config_name = f"{name}.apps.{app_config_name}"

                transformer = Transformation(root_path=self.folder)
                operation = AppendToList(name="INSTALLED_APPS", value=f'"{fully_qualified_app_config_name}"')
                transformer.modify_file(path=settings_path, operation=operation)

                stdout(f"✅ [blue]{fully_qualified_app_config_name}[/blue] added to [blue]INSTALLED_APPS[/blue]")
            else:
                logger.error("app_config_name could not be determined")
        else:
            logger.error("apps.py doesn't exist")


class ApiAppCreator(AppCreator):
    default_app_name = "api"

    def create(self) -> None:
        super().create()

        # Add urls.py
        urls_template_file = TemplateFile(self.folder / self.app_name / "urls.py", {"app_name": self.app_name})
        create_file(template_file=urls_template_file, resource_path="templates/app_template")


class WebAppCreator(AppCreator):
    default_app_name = "web"

    def create(self) -> None:
        super().create()

        # Create project-level folder for static files
        if not (self.folder / "static").exists():
            (self.folder / "static/css").mkdir(parents=True, exist_ok=True)
            (self.folder / "static/js").mkdir(parents=True, exist_ok=True)
            (self.folder / "static/img").mkdir(parents=True, exist_ok=True)

        # Create urls.py
        urls_template_file = TemplateFile(self.folder / self.app_name / "urls.py", {"app_name": self.app_name})
        create_file(template_file=urls_template_file, resource_path="templates/app_template")

        # Create folder for templates
        (self.folder / self.app_name / "templates" / self.app_name).mkdir(parents=True, exist_ok=True)
        urls_template_file = TemplateFile(
            self.folder / self.app_name / "templates" / self.app_name / "index.html",
            {"app_name": self.app_name},
        )
        create_file(template_file=urls_template_file, resource_path="templates/app_template")

        # Create folder for templatetags
        (self.folder / self.app_name / "templatetags").mkdir(parents=True, exist_ok=True)
        (self.folder / self.app_name / "templatetags" / "__init__.py").touch(exist_ok=True)


class WorkerAppCreator(AppCreator):
    default_app_name = "worker"

    def create(self) -> None:
        super().create()

        # Create tasks.py
        create_file(template_file=TemplateFile(path=self.folder / self.app_name / "tasks.py"))

        # Remove default views.py
        (self.folder / self.app_name / "views.py").unlink(missing_ok=True)
