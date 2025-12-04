import pytest

from django_new.transformer.operations.toml import AddKeyValue


def test_existing_key():
    expected = """
[project]
name = "new-name"
version = "0.1.0"
    """

    content = """
[project]
name = "test"
version = "0.1.0"
    """

    operation = AddKeyValue(name="project", key="name", value="new-name")

    actual = operation.apply(content)

    assert expected == actual


def test_new_table():
    expected = """
[project]
name = "test"
version = "0.1.0"

[dependencies]
pytest = "^7.0"
"""

    content = """
[project]
name = "test"
version = "0.1.0"
"""

    operation = AddKeyValue(name="dependencies", key="pytest", value="^7.0")

    actual = operation.apply(content)

    # Verify
    assert expected == actual


def test_description():
    expected = "Add pytest = '^7.0' to [tool.poetry.dependencies]"

    operation = AddKeyValue(name="tool.poetry.dependencies", key="pytest", value="^7.0")
    actual = operation.description()

    assert expected == actual
