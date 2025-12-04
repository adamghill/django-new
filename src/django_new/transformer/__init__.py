import logging
from pathlib import Path

from django_new.transformer.operations import Operation

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

    def modify_file(self, path: str | Path, operation: Operation):
        """Apply an operation to a file"""

        if isinstance(path, str):
            path = Path(path)

        path = (self.root_path / path).resolve()
        self.assert_path_is_valid(path)

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
