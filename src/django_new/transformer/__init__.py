import importlib
import inspect
import logging
from pathlib import Path
from typing import Any

from django_new.transformer.operations import Operation
from django_new.transformer.operations.python import GetVariable as PythonGetVariable
from django_new.transformer.operations.toml import GetVariable as TomlGetVariable

logger = logging.getLogger(__name__)


class Transformation:
    """Base class for transformations"""

    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self._changes = []

    def forwards(self):
        """Apply the migration"""

        raise NotImplementedError

    def backwards(self):
        """Reverse the migration"""

        raise NotImplementedError

    def assert_path_is_valid(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Check if the path is within the root directory
        try:
            path.relative_to(self.root_path.resolve())
        except ValueError as e:
            raise ValueError(f"Path '{path}' is not within the project root '{self.root_path}'") from e

    def get_path(self, path: str | Path) -> Path:
        if isinstance(path, str):
            path = Path(path)

        path = (self.root_path / path).resolve()
        self.assert_path_is_valid(path)

        return path

    def get_settings_file(self) -> Path:
        """Get the path to the settings file."""

        paths = [
            self.root_path / "config/settings.py",
            self.root_path / "config/settings/base.py",
            self.root_path / "settings/base.py",
            self.root_path / "settings.py",
        ]

        for path in paths:
            if path.exists():
                return path

        raise FileNotFoundError("settings file not found")

    def get_variable(self, path: str | Path, variable_name: str) -> Any:
        """Get the value of a variable from a file"""

        path = self.get_path(path)

        # Read current content
        content = path.read_text()

        for operation_class in [TomlGetVariable, PythonGetVariable]:
            operation = operation_class(name=variable_name)

            if operation.can_handle(path=path):
                try:
                    return operation.apply(content=content)
                except Exception:
                    raise

        raise ValueError(f"Variable '{variable_name}' not found in file '{path}'")

    def modify_file(self, path: str | Path, operation: Operation):
        """Apply an operation to a file"""

        path = self.get_path(path)

        if not operation.can_handle(path):
            raise ValueError(f"Operation {type(operation).__name__} cannot handle file {path}")

        # Read current content
        content = path.read_text()

        # Store original for rollback
        self._changes.append((path, content))

        # Apply operation
        new_content = operation.apply(content)

        # Write new content to file
        path.write_text(new_content)

    def rollback_changes(self):
        """Rollback all changes made during this session"""

        for path, original_content in reversed(self._changes):
            path.write_text(original_content)

        self._changes.clear()

    def get_next_steps(self) -> list[str]:
        """Get a list of next steps for the transformation. Each item in the list should be Markdown."""

        return []

    def get_summary(self) -> str:
        """Get a summary of the transformation. Should be Markdown."""

        return ""


def resolve_transformation(name: str) -> type[Transformation]:
    """
    Resolve a transformation class from a string.
    The string can be a short name (e.g. "whitenoise") which looks in
    django_new.transformer.transformations, or a dotted path.
    """

    module_path = name

    if "." not in name:
        module_path = f"django_new.transformer.transformations.{name}"

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not import transformation module '{name}'") from e

    # Find a class that inherits from Transformation
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Transformation) and obj is not Transformation:
            return obj

    raise ValueError(f"No Transformation class found in module '{module_path}'")


class Runner:
    """Runs transformations."""

    def __init__(self, path: Path, dry_run: bool = False):  # noqa: FBT001, FBT002
        self.path = path
        self.dry_run = dry_run

        # Track operations in dry-run mode
        self._operations = []

    def install(self, *transformations: list[Transformation]) -> bool:
        """Run forwards transformations."""

        for transformation in transformations:
            if self.dry_run:
                # Intercept operations for dry run
                original_modify = transformation.modify_file

                def track_operation(filepath, operation):
                    self._operations.append((filepath, operation))

                transformation.modify_file = track_operation

                try:
                    transformation.forwards()

                    return self._operations
                finally:
                    transformation.modify_file = original_modify
            else:
                try:
                    transformation.forwards()
                except Exception as e:
                    logger.exception(e)
                    transformation.rollback_changes()

                    raise

        return True

    def uninstall(self, *transformations: list[Transformation]) -> bool:
        """Run backwards transformations."""

        for transformation in transformations:
            if self.dry_run:
                original_modify = transformation.modify_file

                def track_operation(filepath, operation):
                    self._operations.append((filepath, operation))

                transformation.modify_file = track_operation

                try:
                    transformation.backwards()

                    return self._operations
                finally:
                    transformation.modify_file = original_modify
            else:
                try:
                    transformation.backwards()

                    return True
                except Exception as e:
                    logger.exception(e)
                    transformation.rollback_changes()

                    raise

        return True
