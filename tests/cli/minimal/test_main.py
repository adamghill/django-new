from unittest.mock import patch

import pytest

from tests.assertions import (
    assert_base_app,
    assert_base_project,
    assert_file,
    assert_file_missing,
)
from tests.utils import call_main


def test(monkeypatch, tmp_path):
    """Create a minimal Django project with the --minimal flag."""

    name = "minimal_project"
    call_main(monkeypatch, tmp_path, name, "--minimal")

    assert_base_project(path=tmp_path, name=name)
    assert_base_app(path=tmp_path / name, app_config_name="MinimalProjectConfig")

    # Verify the app was added to INSTALLED_APPS
    assert_file(tmp_path / name / "settings.py", '"minimal_project.apps.MinimalProjectConfig"')


def test_existing_project(monkeypatch, tmp_path):
    """Creating a minimal project should fail if a project already exists."""

    name = "existing_project"
    call_main(monkeypatch, tmp_path, name, "--project")

    # Try to create a minimal project in the same directory
    with patch("django_new.cli.stderr") as mock_stderr:
        with pytest.raises(SystemExit) as excinfo:
            call_main(monkeypatch, tmp_path, "new_minimal_project", "--minimal")

        assert excinfo.value.code == 1
        mock_stderr.assert_called_once()


def test_invalid_name(monkeypatch, tmp_path):
    """Creating a minimal project with an invalid name should fail."""

    name = "invalid-name"  # Contains a dash which is not allowed

    with patch("django_new.cli.stderr") as mock_stderr:
        with pytest.raises(SystemExit) as excinfo:
            call_main(monkeypatch, tmp_path, name, "--minimal")

        assert excinfo.value.code == 1
        mock_stderr.assert_called_once()


def test_api(monkeypatch, tmp_path):
    """Creating a minimal project with the --api flag."""

    name = "minimal_api"
    call_main(monkeypatch, tmp_path, name, "--minimal", "--api")

    assert_base_project(path=tmp_path, name=name)
    assert_base_app(path=tmp_path / name, app_config_name="MinimalApiConfig")

    assert_file_missing(tmp_path / name / "api")  # API directory should not exist

    # Verify the app was added to INSTALLED_APPS
    assert_file(tmp_path / name / "settings.py", '"minimal_api.apps.MinimalApiConfig"')
