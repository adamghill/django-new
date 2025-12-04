import pytest

from django_new.transformer.operations.python import GetVariable


def test_get_top_level_string():
    """Test getting a top-level string variable"""
    content = """
STATIC_ROOT = "/var/www/static"
"""

    operation = GetVariable(name="STATIC_ROOT")
    actual = operation.apply(content)

    assert actual == '"/var/www/static"'


def test_get_top_level_number():
    """Test getting a top-level number variable"""
    content = """
DEBUG = True
PORT = 8000
"""

    operation = GetVariable(name="PORT")
    actual = operation.apply(content)

    assert actual == "8000"


def test_get_top_level_boolean():
    """Test getting a top-level boolean variable"""
    content = """
DEBUG = True
"""

    operation = GetVariable(name="DEBUG")
    actual = operation.apply(content)

    assert actual == "True"


def test_get_top_level_list():
    """Test getting a top-level list variable"""
    content = """
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
"""

    operation = GetVariable(name="ALLOWED_HOSTS")
    actual = operation.apply(content)

    assert actual == '["localhost", "127.0.0.1"]'


def test_get_top_level_dict():
    """Test getting a top-level dict variable"""
    content = """
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}
"""

    operation = GetVariable(name="DATABASES")
    actual = operation.apply(content)

    # Check that the dict structure is preserved
    assert '"default"' in actual
    assert '"ENGINE"' in actual
    assert '"django.db.backends.sqlite3"' in actual


def test_get_nested_class_attribute():
    """Test getting an attribute from a nested class"""
    content = """
class Settings:
    STATIC_ROOT = "/var/www/static"
    DEBUG = False
"""

    operation = GetVariable(name="Settings.STATIC_ROOT")
    actual = operation.apply(content)

    assert actual == '"/var/www/static"'


def test_get_nested_class_list():
    """Test getting a list from a nested class"""
    content = """
class Settings:
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
    ]
"""

    operation = GetVariable(name="Settings.INSTALLED_APPS")
    actual = operation.apply(content)

    assert '"django.contrib.admin"' in actual
    assert '"django.contrib.auth"' in actual


def test_get_nonexistent_attribute_raises():
    """Test that getting a nonexistent attribute raises ValueError"""
    content = """
SOME_VAR = 123
"""

    operation = GetVariable(name="NON_EXISTENT")

    with pytest.raises(ValueError, match="Variable 'NON_EXISTENT' not found in file"):
        operation.apply(content)


def test_get_attribute_from_wrong_class_raises():
    """Test that getting an attribute from the wrong class raises ValueError"""
    content = """
class Settings:
    DEBUG = True

class OtherClass:
    OTHER_VAR = False
"""

    operation = GetVariable(name="OtherClass.DEBUG")

    with pytest.raises(ValueError, match="Variable 'OtherClass.DEBUG' not found in file"):
        operation.apply(content)


def test_description():
    """Test the description method"""
    operation = GetVariable(name="STATIC_ROOT")
    assert operation.description() == "Get value of STATIC_ROOT"

    operation = GetVariable(name="Settings.DEBUG")
    assert operation.description() == "Get value of Settings.DEBUG"


def test_get_with_multiple_variables():
    """Test getting a specific variable when multiple exist"""
    content = """
VAR1 = "first"
VAR2 = "second"
VAR3 = "third"
"""

    operation = GetVariable(name="VAR2")
    actual = operation.apply(content)

    assert actual == '"second"'


def test_get_attribute_with_complex_value():
    """Test getting an attribute with a complex expression"""
    content = """
BASE_DIR = Path(__file__).resolve().parent.parent
"""

    operation = GetVariable(name="BASE_DIR")
    actual = operation.apply(content)

    # Should preserve the expression
    assert "Path" in actual
    assert "__file__" in actual
    assert "resolve()" in actual


def test_get_attribute_from_nested_class_with_multiple_classes():
    """Test getting an attribute when multiple classes exist"""
    content = """
class FirstClass:
    VALUE = "first"

class SecondClass:
    VALUE = "second"
"""

    operation = GetVariable(name="SecondClass.VALUE")
    actual = operation.apply(content)

    assert actual == '"second"'


def test_get_multiline_string():
    """Test getting a multiline string variable"""
    content = '''
DESCRIPTION = """
This is a multiline
string value
"""
'''

    operation = GetVariable(name="DESCRIPTION")
    actual = operation.apply(content)

    assert "multiline" in actual
    assert "string value" in actual
