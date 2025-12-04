import pytest

from django_new.transformer.operations.python import AppendToList


def test_append_to_top_level_list():
    expected = """
SOME_VAR = ["django"]
"""

    content = """
SOME_VAR = []
"""

    operation = AppendToList(name="SOME_VAR", value='"django"')
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_existing_list():
    expected = """
SOME_VAR = ["django", "pytest"]
"""

    content = """
SOME_VAR = ["django"]
"""

    operation = AppendToList(name="SOME_VAR", value='"pytest"')
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_nested_class_list():
    expected = """
class Settings:
    INSTALLED_APPS = ["django", "pytest"]
"""

    content = """
class Settings:
    INSTALLED_APPS = ["django"]
"""

    operation = AppendToList(name="Settings.INSTALLED_APPS", value='"pytest"')
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_list_with_position():
    expected = """
SOME_VAR = ["pytest", "django"]
"""

    content = """
SOME_VAR = ["django"]
"""

    operation = AppendToList(name="SOME_VAR", value='"pytest"', position=0)
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_nonexistent_list_raises():
    content = """
SOME_OTHER_VAR = 123
"""

    operation = AppendToList(name="NON_EXISTENT", value='"value"')

    with pytest.raises(ValueError, match="List 'NON_EXISTENT' not found in file"):
        operation.apply(content)


def test_append_to_non_list_raises():
    content = """
NOT_A_LIST = 123
"""

    operation = AppendToList(name="NOT_A_LIST", value='"value"')

    with pytest.raises(ValueError, match="List 'NOT_A_LIST' not found in file"):
        operation.apply(content)


def test_description():
    operation = AppendToList(name="MY_LIST", value='"value"', position=1)
    assert operation.description() == 'Append "value" to MY_LIST at position 1'

    operation = AppendToList(name="MY_LIST", value='"value"')
    assert operation.description() == 'Append "value" to MY_LIST'


def test_append_with_negative_position():
    """Test appending with negative position (insert before last element)"""
    content = """
SOME_VAR = ["django", "pytest"]
"""

    operation = AppendToList(name="SOME_VAR", value='"new_item"', position=-1)
    actual = operation.apply(content)

    # Negative position should insert before the end
    assert '"new_item"' in actual
    assert '"django"' in actual
    assert '"pytest"' in actual


def test_append_with_large_negative_position():
    """Test appending with large negative position (should insert at beginning)"""
    expected = """
SOME_VAR = ["new_item", "django", "pytest"]
"""

    content = """
SOME_VAR = ["django", "pytest"]
"""

    operation = AppendToList(name="SOME_VAR", value='"new_item"', position=-10)
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_deeply_nested_class():
    """Test appending to a list in a nested class structure"""
    content = """
class Outer:
    class Inner:
        MY_LIST = ["item1"]
"""

    # Note: nested class lists need the outer class prefix
    operation = AppendToList(name="Outer.Inner.MY_LIST", value='"item2"')
    actual = operation.apply(content)

    # Just verify the item was added
    assert '"item2"' in actual
    assert '"item1"' in actual


def test_append_to_list_with_complex_attribute_path():
    """Test appending to a list accessed via complex attribute path"""
    content = """
class Config:
    DATABASES = ["sqlite"]
"""

    operation = AppendToList(name="Config.DATABASES", value='"postgres"')
    actual = operation.apply(content)

    assert '"postgres"' in actual
    assert '"sqlite"' in actual


def test_append_with_position_beyond_list_length():
    """Test that position beyond list length appends at end"""
    expected = """
SOME_VAR = ["django", "pytest", "new_item"]
"""

    content = """
SOME_VAR = ["django", "pytest"]
"""

    operation = AppendToList(name="SOME_VAR", value='"new_item"', position=100)
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()
