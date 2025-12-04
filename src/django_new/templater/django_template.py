import logging
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

from django.template import Context, Engine

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TemplateFile:
    """A template file to be rendered.

    The template file extension should end with '-tpl'.
    """

    path: Path
    context: dict[str, Any] = field(default_factory=dict)


def create_file(
    template_file: TemplateFile,
    resource_name: str = "django_new",
    resource_path: str = "templates",
):
    """Create file based on a DTL template in a specified resource."""

    logger.debug(f"Create file, {template_file.path}, if it doesn't exist")

    if template_file.path.exists():
        logger.debug(f"Do not create template file, {template_file.path}, because it already exists")
    else:
        engine = Engine(debug=False, autoescape=False)

        template_name = template_file.path.name + "-tpl"
        logger.debug(f"Template name: {template_name}")

        template_path = resources.files(resource_name) / resource_path / template_name
        template_content = template_path.read_text()
        logger.debug("Read template content")

        template_content = "{% autoescape off %}" + template_content + "{% endautoescape %}"
        logger.debug("Wrap template content in autoescape off")

        template = engine.from_string(template_content)
        rendered_content = template.render(Context(template_file.context or {}))
        logger.debug(f"Render template content with context {template_file.context}")

        template_file.path.write_text(rendered_content)
        logger.debug(f"Created template file, {template_file.path}")
