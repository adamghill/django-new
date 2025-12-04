import pytest

from django_new.transformer.operations.toml import RemoveKey


def test_remove_key():
    expected = """
[project]
version = "0.1.0"
"""

    content = """
[project]
name = "test"
version = "0.1.0"
"""

    operation = RemoveKey(table_path="project", key="name")
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_remove_key_from_nested_table():
    expected = """
[project]
version = "0.1.0"

[tool.poetry]
author = "Test User"
"""

    content = """
[project]
version = "0.1.0"

[tool.poetry]
name = "test"
author = "Test User"
"""

    operation = RemoveKey(table_path="tool.poetry", key="name")
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_remove_nonexistent_key_raises():
    content = """
[project]
name = "test"
"""

    operation = RemoveKey(table_path="project", key="version")

    with pytest.raises(ValueError, match="Key 'version' not found in 'project'"):
        operation.apply(content)


def test_remove_from_nonexistent_table_raises():
    content = """
[project]
name = "test"
"""

    operation = RemoveKey(table_path="nonexistent", key="key")

    with pytest.raises(ValueError, match="Table path 'nonexistent' not found"):
        operation.apply(content)


def test_description():
    operation = RemoveKey(table_path="project", key="name")

    assert operation.description() == "Remove name from [project]"
