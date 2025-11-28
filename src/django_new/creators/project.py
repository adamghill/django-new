import logging
from pathlib import Path
from shutil import rmtree

from django_new.creators.app import CLASSIC_CONFIGURATION_PATH_NAME, AppCreator
from django_new.templater.django_template import TemplateFile, create_file
from django_new.utils import call_command, stderr, stdout_success

logger = logging.getLogger(__name__)


class ProjectCreator:
    def __init__(self, name: str, folder: Path):
        self.name = name
        self.folder = folder

    def create(self, display_name: str | None = None):
        """Create a new Django project."""

        call_command("startproject", self.name, self.folder)
        stdout_success("✅ Project created", style="green")

        # Create additional files needed for a new Django project that are not included with `startproject`
        project_name = display_name or self.name

        created_files = []
        template_files = (
            TemplateFile(self.folder / "pyproject.toml", {"name": project_name}),
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
            stdout_success(f"✅ {', '.join(created_files)} files created")


class ClassicProjectCreator(ProjectCreator):
    def __init__(self, folder: str):
        super().__init__(name=CLASSIC_CONFIGURATION_PATH_NAME, folder=folder)


class MinimalProjectCreator(ProjectCreator):
    def __init__(self, name: str, folder: str):
        super().__init__(name=name, folder=folder)

    def create(self):
        super().create()

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
