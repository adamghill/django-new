from pathlib import Path

from django_new.transformer.operations.python import PythonOperation


# Create a concrete implementation for testing
class FakePythonOperation(PythonOperation):
    """Concrete implementation for testing PythonOperation"""

    def description(self) -> str:
        return "Test operation"

    def apply(self, content: str) -> str:
        return content


def test_python():
    """Test that can_handle returns True for .py files"""
    operation = FakePythonOperation()

    assert operation.can_handle(Path("test.py")) is True
    assert operation.can_handle(Path("/path/to/file.py")) is True
    assert operation.can_handle(Path("module/__init__.py")) is True


def test_non_python():
    """Test that can_handle returns False for non-Python files"""
    operation = FakePythonOperation()

    assert operation.can_handle(Path("test.txt")) is False
    assert operation.can_handle(Path("requirements.txt")) is False
    assert operation.can_handle(Path("setup.cfg")) is False
    assert operation.can_handle(Path("README.md")) is False


def test_case_insensitive():
    """Test that can_handle is case-insensitive for file extensions"""
    operation = FakePythonOperation()

    assert operation.can_handle(Path("test.PY")) is True
    assert operation.can_handle(Path("module/__INIT__.PY")) is True


def test_no_extension():
    """Test that can_handle handles files with no extension"""

    operation = FakePythonOperation()

    assert operation.can_handle(Path("no_extension")) is False
    assert operation.can_handle(Path("path/to/file")) is False
