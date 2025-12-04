import logging
from pathlib import Path
from shutil import rmtree

from django_new.creators.app import CLASSIC_CONFIGURATION_PATH_NAME, AppCreator
from django_new.templater.django_template import TemplateFile, create_file
from django_new.utils import call_command, stderr, stdout

logger = logging.getLogger(__name__)


class ProjectCreator:
    def __init__(self, name: str, folder: Path):
        self.name = name
        self.folder = folder

    def create(self, display_name: str | None = None, python_version: str = ">=3.10", django_version: str = ">=5"):
        """Create a new Django project.

        Args:
            display_name: The display name of the project (defaults to the project name)
            python_version: Python version requirement string (e.g., '>=3.10')
            django_version: Django version requirement string (e.g., '>=5')
        """

        call_command("startproject", self.name, self.folder)
        stdout("✅ Project created")

        # Create `tests` directory and basic test configuration
        (self.folder / "tests").mkdir(exist_ok=True)
        (self.folder / "tests" / "__init__.py").write_text("")

        # Create additional files for new Django projects that are not included with `startproject`
        project_name = display_name or self.name

        created_files = []
        template_files = (
            TemplateFile(
                self.folder / "pyproject.toml",
                {"name": project_name, "python_version": python_version, "django_version": django_version},
            ),
            TemplateFile(self.folder / "README.md", {"name": project_name}),
            TemplateFile(self.folder / ".gitignore"),
            TemplateFile(self.folder / ".env"),
        )

        for template_file in template_files:
            try:
                create_file(template_file=template_file)
                created_files.append(template_file.path.name)
            except Exception as e:
                stderr(str(e))
                continue

        if created_files:
            files = ""

            for idx, file in enumerate(created_files):
                files += f"[blue]{file}[/blue]"

                if idx == len(created_files) - 2:
                    files += ", and "
                elif idx != len(created_files) - 1:
                    files += ", "

            stdout(f"✅ {files} created")


class TemplateProjectCreator(ProjectCreator):
    def __init__(self, name: str, folder: str):
        super().__init__(name=name, folder=folder)

    def create(self, project_template: str, python_version: str = ">=3.10", django_version: str = ">=5"):
        """Create a new Django project from a template.

        Args:
            project_template: The template to use for the project (URL or local path)
            python_version: Python version requirement string (e.g., '>=3.10')
            django_version: Django version requirement string (e.g., '>=5')
        """
        call_command("startproject", self.name, self.folder, f"--template={project_template}")
        stdout("✅ Project created from template")

        # Create additional files
        project_name = self.name
        created_files = []
        template_files = (
            TemplateFile(
                self.folder / "pyproject.toml",
                {"name": project_name, "python_version": python_version, "django_version": django_version},
            ),
            TemplateFile(self.folder / "README.md", {"name": project_name}),
            TemplateFile(self.folder / ".gitignore"),
            TemplateFile(self.folder / ".env"),
        )

        for template_file in template_files:
            try:
                if not template_file.path.exists():
                    create_file(template_file=template_file)
                    created_files.append(template_file.path.name)
            except Exception as e:
                stderr(str(e))


class ClassicProjectCreator(ProjectCreator):
    def __init__(self, folder: str):
        super().__init__(name=CLASSIC_CONFIGURATION_PATH_NAME, folder=folder)


class MinimalProjectCreator(ProjectCreator):
    def __init__(self, name: str, folder: str):
        super().__init__(name=name, folder=folder)

    def create(self, python_version: str = ">=3.10", django_version: str = ">=5"):
        """Create a minimal Django project.

        Args:
            python_version: Python version requirement string (e.g., '>=3.10')
            django_version: Django version requirement string (e.g., '>=5')
        """
        super().create(python_version=python_version, django_version=django_version)

        # TOOD: Support api, web, worker flags with minimal projects
        AppCreator(app_name=self.name, folder=self.folder / self.name).create()

        logger.debug("Move app to project folder")
        for item in (self.folder / self.name / self.name).iterdir():
            target = (self.folder / self.name) / item.name

            if not target.exists():
                logger.debug(f"Move {item} -> {target}")
                item.replace(target)

        logger.debug("Remove temporary app directory")
        rmtree(self.folder / self.name / self.name, ignore_errors=True)
        logger.debug("Finished cleaning up temporary app directory")
