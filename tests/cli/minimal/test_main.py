from unittest.mock import patch

from typer.testing import CliRunner

from django_new.cli import app
from tests.assertions import (
    assert_base_app,
    assert_base_project,
    assert_file,
    assert_file_missing,
)

runner = CliRunner(catch_exceptions=False)


def test(tmp_path):
    """Create a minimal Django project with the --minimal flag."""

    name = "minimal_project"
    result = runner.invoke(app, [name, str(tmp_path), "--minimal"])

    assert result.exit_code == 0

    assert_base_project(path=tmp_path, name=name)
    assert_base_app(path=tmp_path / name, app_config_name="MinimalProjectConfig")

    # Verify the app was added to INSTALLED_APPS
    assert_file(tmp_path / name / "settings.py", '"minimal_project.apps.MinimalProjectConfig"')


def test_existing_project(tmp_path):
    """Creating a minimal project should fail if a project already exists."""

    name = "existing_project"
    result = runner.invoke(app, [name, str(tmp_path), "--project"])

    assert result.exit_code == 0

    # Try to create a minimal project in the same directory
    with patch("django_new.cli.stderr") as mock_stderr:
        result = runner.invoke(app, ["new_minimal_project", str(tmp_path), "--minimal"])

        assert result.exit_code == 1
        mock_stderr.assert_called_once()


def test_invalid_name(tmp_path):
    """Creating a minimal project with an invalid name should fail."""

    name = "invalid-name"  # Contains a dash which is not allowed
    result = runner.invoke(app, [name, str(tmp_path), "--minimal"], input="y\n")

    assert result.exit_code == 0

    assert_base_project(path=tmp_path, name="invalid_name")
    assert_base_app(path=tmp_path / "invalid_name", app_config_name="InvalidNameConfig")


def test_api(tmp_path):
    """Creating a minimal project with the --api flag."""

    name = "minimal_api"
    result = runner.invoke(app, [name, str(tmp_path), "--minimal", "--api"])

    assert result.exit_code == 0

    assert_base_project(path=tmp_path, name=name)
    assert_base_app(path=tmp_path / name, app_config_name="MinimalApiConfig")

    assert_file_missing(tmp_path / name / "api")  # API directory should not exist

    # Verify the app was added to INSTALLED_APPS
    assert_file(tmp_path / name / "settings.py", '"minimal_api.apps.MinimalApiConfig"')
