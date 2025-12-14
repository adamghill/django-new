from pathlib import Path

import pytest

from django_new.transformer import Runner, Transformation
from django_new.transformer.operations.python import AppendToList, RemoveFromList


class FakeTransformation(Transformation):
    """Test transformation for testing"""

    def __init__(self, root_path: Path, *, should_fail: bool = False):
        super().__init__(root_path)
        self.should_fail = should_fail
        self.forwards_called = False
        self.backwards_called = False

    def forwards(self):
        self.forwards_called = True

        if self.should_fail:
            raise ValueError("Intentional failure")

        operation = AppendToList(name="INSTALLED_APPS", value='"myapp"')
        self.modify_file(path="settings.py", operation=operation)

    def backwards(self):
        self.backwards_called = True

        if self.should_fail:
            raise ValueError("Intentional failure")

        operation = RemoveFromList(name="INSTALLED_APPS", value='"myapp"')
        self.modify_file(path="settings.py", operation=operation)


def test_install(fake_fs, temp_path):
    """Test install"""

    expected = 'INSTALLED_APPS = ["myapp"]'

    settings = temp_path / "settings.py"
    original_content = "INSTALLED_APPS = []"
    settings.write_text(original_content)

    runner = Runner(path=temp_path, dry_run=False)
    transformation = FakeTransformation(root_path=temp_path)

    actual = runner.install(transformation)

    assert actual is True
    assert transformation.forwards_called

    assert expected == settings.read_text()


def test_install_with_error(fake_fs, temp_path):
    """Test that install rolls back on error"""

    settings = temp_path / "settings.py"
    original_content = "INSTALLED_APPS = []"
    settings.write_text(original_content)

    runner = Runner(path=temp_path, dry_run=False)
    transformation = FakeTransformation(root_path=temp_path, should_fail=True)

    with pytest.raises(ValueError, match="Intentional failure"):
        runner.install(transformation)

    # File should be rolled back to original
    assert original_content == settings.read_text()


def test_install_dry_run(fake_fs, temp_path):
    """Test that install in dry-run mode returns operations"""

    settings = temp_path / "settings.py"
    original_content = "INSTALLED_APPS = []"
    settings.write_text(original_content)

    runner = Runner(path=temp_path, dry_run=True)
    transformation = FakeTransformation(root_path=temp_path)

    actual = runner.install(transformation)

    assert transformation.forwards_called
    assert len(actual) == 1
    assert len(actual[0]) == 2
    assert actual[0][0] == "settings.py"
    assert actual[0][1].__class__ == AppendToList

    # File should be rolled back to original
    assert original_content == settings.read_text()


def test_uninstall(fake_fs, temp_path):
    """Test uninstalling a single transformation"""

    expected = """
INSTALLED_APPS = [
    "django.contrib.admin",
    
]
"""  # noqa: W293

    # Create a settings file with an app
    settings = temp_path / "settings.py"
    settings.write_text("""
INSTALLED_APPS = [
    "django.contrib.admin",
    "myapp",
]
""")

    runner = Runner(path=temp_path, dry_run=False)
    transformation = FakeTransformation(root_path=temp_path)

    actual = runner.uninstall(transformation)

    assert actual is True
    assert transformation.backwards_called

    assert expected == settings.read_text()


def test_uninstall_dry_run(fake_fs, temp_path):
    """Test uninstalling a single transformation in dry-run mode"""

    # Create a settings file with an app
    settings = temp_path / "settings.py"
    original_content = """
INSTALLED_APPS = [
    "django.contrib.admin",
    "myapp",
]
"""
    settings.write_text(original_content)

    runner = Runner(path=temp_path, dry_run=True)
    transformation = FakeTransformation(root_path=temp_path)

    actual = runner.uninstall(transformation)

    assert transformation.backwards_called
    assert len(actual) == 1
    assert len(actual[0]) == 2
    assert actual[0][0] == "settings.py"
    assert actual[0][1].__class__ == RemoveFromList

    assert original_content == settings.read_text()


def test_uninstall_with_error(fake_fs, temp_path):
    """Test that uninstall rolls back on error"""

    settings = temp_path / "settings.py"
    original_content = """
INSTALLED_APPS = [
    "django.contrib.admin",
    "myapp",
]
"""
    settings.write_text(original_content)

    runner = Runner(path=temp_path, dry_run=False)
    transformation = FakeTransformation(root_path=temp_path, should_fail=True)

    with pytest.raises(ValueError, match="Intentional failure"):
        runner.uninstall(transformation)

    # File should be rolled back to original
    assert original_content == settings.read_text()
