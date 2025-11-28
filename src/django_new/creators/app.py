import logging
from pathlib import Path

from django_new.formatters.adder import add_to_list
from django_new.parser import get_class_name
from django_new.templater.django_template import TemplateFile, create_file
from django_new.utils import call_command, stdout_success

logger = logging.getLogger(__name__)


CLASSIC_CONFIGURATION_PATH_NAME = "config"


class AppCreator:
    def __init__(self, app_name: str | None, folder: Path):
        self.app_name = app_name

        if self.app_name is None:
            self.app_name = self.default_app_name

        assert self.app_name, "App name is unknown"

        self.folder = folder

    def create(self) -> None:
        """Create a new Django app."""

        logger.debug(f"Start creating app, {self.app_name}")

        logger.debug(f"Create app directory, {self.folder / self.app_name}, if it doesn't exist")
        (self.folder / self.app_name).mkdir(parents=True, exist_ok=True)

        call_command("startapp", self.app_name, self.folder / self.app_name)
        (self.folder / self.app_name / "urls.py").write_text("# urls.py")

        (self.folder / self.app_name / "tests.py").unlink(missing_ok=True)

        # if not is_quiet:
        #     print_success(f"✅ `{name}` app created")

        apps_path = self.folder / self.app_name / "apps.py"
        settings_path = self.folder / "settings.py"

        if not settings_path.exists():
            settings_path = self.folder / CLASSIC_CONFIGURATION_PATH_NAME / "settings.py"

        if settings_path.exists():
            self.add_app_to_installed_apps(name=self.app_name, apps_path=apps_path, settings_path=settings_path)

    def add_app_to_installed_apps(self, name: str, apps_path: Path, settings_path: Path):
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
                stdout_success(f"✅ {fully_qualified_app_config_name} added to INSTALLED_APPS")
            else:
                logger.error("app_config_name could not be determined")
        else:
            logger.error("apps.py doesn't exist")


class ApiAppCreator(AppCreator):
    default_app_name = "api"

    def create(self) -> None:
        super().create()


class WebAppCreator(AppCreator):
    default_app_name = "web"

    def create(self) -> None:
        super().create()

        # Create folder for static files
        (self.folder / "static/css").mkdir(parents=True, exist_ok=True)
        (self.folder / "static/js").mkdir(parents=True, exist_ok=True)
        (self.folder / "static/img").mkdir(parents=True, exist_ok=True)

        # Create folder for templates
        (self.folder / self.app_name / "templates" / self.app_name).mkdir(parents=True, exist_ok=True)
        # TODO: Use tpl template files to create something here
        (self.folder / self.app_name / "templates" / self.app_name / "base.html").touch(exist_ok=True)
        (self.folder / self.app_name / "templates" / self.app_name / "index.html").touch(exist_ok=True)

        # Create folder for templatetags
        (self.folder / self.app_name / "templatetags").mkdir(parents=True, exist_ok=True)
        (self.folder / self.app_name / "templatetags" / "__init__.py").touch(exist_ok=True)


class WorkerAppCreator(AppCreator):
    default_app_name = "worker"

    def create(self) -> None:
        super().create()

        # Create tasks.py
        create_file(template_file=TemplateFile(path=self.folder / self.app_name / "tasks.py"))

        # Remove views.py and urls.py
        (self.folder / self.app_name / "views.py").unlink(missing_ok=True)
        (self.folder / self.app_name / "urls.py").unlink(missing_ok=True)
