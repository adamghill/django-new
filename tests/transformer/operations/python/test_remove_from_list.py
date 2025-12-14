import pytest

from django_new.transformer.operations.python import RemoveFromList


def test_remove_from_top_level_list():
    expected = """
SOME_VAR = []
"""

    content = """
SOME_VAR = ["django"]
"""

    operation = RemoveFromList(name="SOME_VAR", value='"django"')
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_remove_from_existing_list():
    expected = """
SOME_VAR = ["pytest"]
"""

    content = """
SOME_VAR = ["django", "pytest"]
"""

    operation = RemoveFromList(name="SOME_VAR", value='"django"')
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_remove_from_nested_class_list():
    expected = """
class Settings:
    INSTALLED_APPS = ["pytest"]
"""

    content = """
class Settings:
    INSTALLED_APPS = ["django", "pytest"]
"""

    operation = RemoveFromList(name="Settings.INSTALLED_APPS", value='"django"')
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_remove_from_nonexistent_list_raises():
    content = """
SOME_OTHER_VAR = 123
"""

    operation = RemoveFromList(name="NON_EXISTENT", value='"value"')

    with pytest.raises(ValueError, match="List 'NON_EXISTENT' not found in file"):
        operation.apply(content)


def test_remove_value_not_in_list_raises():
    content = """
SOME_VAR = ["other"]
"""

    operation = RemoveFromList(name="SOME_VAR", value='"value"')

    with pytest.raises(ValueError, match="Value \"value\" not found in 'SOME_VAR'"):
        operation.apply(content)


def test_description():
    operation = RemoveFromList(name="MY_LIST", value='"value"')
    assert operation.description() == 'Remove "value" from MY_LIST'
