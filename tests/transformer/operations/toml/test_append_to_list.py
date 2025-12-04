import pytest

from django_new.transformer.operations.toml import AppendToList


def test_append_to_top_level_list():
    expected = """
[project]
dependencies = ["django"]
"""

    content = """
[project]
dependencies = []
"""

    operation = AppendToList(name="project.dependencies", value="django")
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_existing_list():
    expected = """
[project]
dependencies = ["django", "pytest"]
"""

    content = """
[project]
dependencies = ["django"]
"""

    operation = AppendToList(name="project.dependencies", value="pytest")
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_nested_list():
    expected = """
[tool.poetry.dependencies]
python = ">=3.8"
packages = ["django", "pytest"]
"""

    content = """
[tool.poetry.dependencies]
python = ">=3.8"
packages = ["django"]
"""

    operation = AppendToList(name="tool.poetry.dependencies.packages", value="pytest")
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_creates_new_list():
    expected = """
[project]
name = "test"
dependencies = ['django']
"""

    content = """
[project]
name = "test"
"""

    operation = AppendToList(name="project.dependencies", value="django")
    actual = operation.apply(content)

    assert actual.strip() == expected.strip()


def test_append_to_non_list_raises():
    content = """
[project]
name = "test"
dependencies = "not-a-list"
"""

    operation = AppendToList(name="project.dependencies", value="django")

    with pytest.raises(ValueError, match="Cannot append to 'dependencies': target is not a list"):
        operation.apply(content)


def test_description():
    operation = AppendToList(name="project.dependencies", value="django")

    assert operation.description() == "Append 'django' to project.dependencies"
