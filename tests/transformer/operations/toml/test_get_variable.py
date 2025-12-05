import pytest

from django_new.transformer.operations.toml import GetVariable


def test_get_top_level_string():
    """Test getting a top-level string value"""
    content = """
[project]
name = "my-project"
version = "0.1.0"
    """

    operation = GetVariable(name="project.name")
    actual = operation.apply(content)

    assert actual == "my-project"


def test_get_top_level_version():
    """Test getting a version number"""
    content = """
[project]
name = "my-project"
version = "0.1.0"
    """

    operation = GetVariable(name="project.version")
    actual = operation.apply(content)

    assert actual == "0.1.0"


def test_get_nested_table_value():
    """Test getting a value from a nested table"""
    content = """
[tool.poetry.dependencies]
python = "^3.9"
django = "^4.2"
    """

    operation = GetVariable(name="tool.poetry.dependencies.python")
    actual = operation.apply(content)

    assert actual == "^3.9"


def test_get_list_value():
    """Test getting a list value"""
    content = """
[project]
dependencies = [
    "django>=4.2",
    "pytest>=7.0",
]
    """

    operation = GetVariable(name="project.dependencies")
    actual = operation.apply(content)

    # Should return a list
    assert isinstance(actual, list)
    assert "django>=4.2" in actual
    assert "pytest>=7.0" in actual


def test_get_table_value():
    """Test getting an entire table/dict value"""
    content = """
[project]
name = "my-project"

[project.urls]
homepage = "https://example.com"
repository = "https://github.com/example/repo"
    """

    operation = GetVariable(name="project.urls")
    actual = operation.apply(content)

    # Should return a dict
    assert isinstance(actual, dict)
    assert actual["homepage"] == "https://example.com"
    assert actual["repository"] == "https://github.com/example/repo"


def test_get_boolean_value():
    """Test getting a boolean value"""
    content = """
[tool.mypy]
strict = true
    """

    operation = GetVariable(name="tool.mypy.strict")
    actual = operation.apply(content)

    assert actual is True


def test_get_integer_value():
    """Test getting an integer value"""
    content = """
[server]
port = 8000
    """

    operation = GetVariable(name="server.port")
    actual = operation.apply(content)

    assert actual == 8000


def test_get_float_value():
    """Test getting a float value"""
    content = """
[settings]
threshold = 3.14
    """

    operation = GetVariable(name="settings.threshold")
    actual = operation.apply(content)

    assert actual == 3.14


def test_get_nonexistent_key_raises():
    """Test that getting a nonexistent key raises ValueError"""
    content = """
[project]
name = "test"
    """

    operation = GetVariable(name="project.nonexistent")

    with pytest.raises(ValueError, match="Key 'nonexistent' not found in table 'project'"):
        operation.apply(content)


def test_get_nonexistent_table_raises():
    """Test that getting from a nonexistent table raises ValueError"""
    content = """
[project]
name = "test"
    """

    operation = GetVariable(name="nonexistent.key")

    with pytest.raises(ValueError, match="Table path 'nonexistent' not found"):
        operation.apply(content)


def test_get_key_from_wrong_table_raises():
    """Test that getting a key from the wrong table raises ValueError"""
    content = """
[project]
name = "test"

[dependencies]
pytest = "^7.0"
    """

    operation = GetVariable(name="project.pytest")

    with pytest.raises(ValueError, match="Key 'pytest' not found in table 'project'"):
        operation.apply(content)


def test_description():
    """Test the description method"""
    operation = GetVariable(name="project.name")
    assert operation.description() == "Get value of project.name"

    operation = GetVariable(name="tool.poetry.dependencies.django")
    assert operation.description() == "Get value of tool.poetry.dependencies.django"


def test_get_deeply_nested_value():
    """Test getting a value from a deeply nested table"""
    content = """
[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
    """

    operation = GetVariable(name="tool.poetry.group.dev.dependencies.pytest")
    actual = operation.apply(content)

    assert actual == "^7.0"


def test_get_multiline_string():
    """Test getting a multiline string value"""
    content = '''
[project]
description = """
This is a multiline
description
"""
    '''

    operation = GetVariable(name="project.description")
    actual = operation.apply(content)

    assert "multiline" in actual
    assert "description" in actual


def test_get_array_of_tables():
    """Test getting an array value"""
    content = """
[project]
authors = [
    {name = "John Doe", email = "john@example.com"},
    {name = "Jane Smith", email = "jane@example.com"},
]
    """

    operation = GetVariable(name="project.authors")
    actual = operation.apply(content)

    # Should return a list of dicts
    assert isinstance(actual, list)
    assert len(actual) == 2
    assert actual[0]["name"] == "John Doe"
    assert actual[1]["email"] == "jane@example.com"
