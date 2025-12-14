from django_new.parser import get_class_name


def test_get_class_name_with_simple_base_class(fake_fs, temp_path):
    """Test finding a class with a simple base class name"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result == "MyAppConfig"


def test_get_class_name_with_dotted_base_class(fake_fs, temp_path):
    """Test finding a class with a fully qualified base class"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
from django.apps import AppConfig

class MyAppConfig(django.apps.AppConfig):
    name = 'myapp'
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result == "MyAppConfig"


def test_get_class_name_with_no_matching_base(fake_fs, temp_path):
    """Test when no class matches the base class"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
class SomeOtherClass:
    pass
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result is None


def test_get_class_name_with_multiple_classes(fake_fs, temp_path):
    """Test finding the first matching class when multiple exist"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
from django.apps import AppConfig

class FirstConfig(AppConfig):
    name = 'first'

class SecondConfig(AppConfig):
    name = 'second'
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result == "FirstConfig"


def test_get_class_name_with_nested_attribute(fake_fs, temp_path):
    """Test finding a class with nested attribute base class"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
import django.apps

class MyAppConfig(django.apps.AppConfig):
    name = 'myapp'
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result == "MyAppConfig"


def test_get_class_name_with_empty_file(fake_fs, temp_path):
    """Test with an empty file"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("")

    result = get_class_name(apps_py, "AppConfig")
    assert result is None


def test_get_class_name_with_no_classes(fake_fs, temp_path):
    """Test with a file containing no classes"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
def some_function():
    pass

SOME_CONSTANT = 42
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result is None


def test_get_class_name_with_wrong_base_class(fake_fs, temp_path):
    """Test when class exists but doesn't inherit from target base"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
class MyClass(SomeOtherBase):
    pass
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result is None


def test_get_class_name_with_multiple_inheritance(fake_fs, temp_path):
    """Test finding a class with multiple base classes"""
    apps_py = temp_path / "apps.py"
    apps_py.write_text("""
from django.apps import AppConfig

class MyAppConfig(SomeMixin, AppConfig):
    name = 'myapp'
""")

    result = get_class_name(apps_py, "AppConfig")
    assert result == "MyAppConfig"
