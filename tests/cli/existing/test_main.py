from unittest.mock import patch

import pytest

from tests.assertions import (
    assert_api,
    assert_app,
    assert_file,
    assert_folder,
    assert_project,
    assert_web,
    assert_worker,
)
from tests.utils import call_main


def _create_project(monkeypatch, tmp_path):
    name = "bare_project"
    call_main(monkeypatch, tmp_path, name, "--project")


def test(monkeypatch, tmp_path):
    """Create an app in an existing classic project."""

    _create_project(monkeypatch, tmp_path)

    name = "new_app"
    call_main(monkeypatch, tmp_path, name)

    assert_app(path=tmp_path / name, app_config_name="NewAppConfig")

    # Ensure that new app got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", f'"{name}.apps.NewAppConfig"')


def test_app(monkeypatch, tmp_path):
    """Create an app in an existing classic project."""

    _create_project(monkeypatch, tmp_path)

    name = "new_app"
    call_main(monkeypatch, tmp_path, name, "--app")

    assert_app(path=tmp_path / name, app_config_name="NewAppConfig")

    # Ensure that new app got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", f'"{name}.apps.NewAppConfig"')


def test_api(monkeypatch, tmp_path):
    """Create an api in an existing classic project."""

    _create_project(monkeypatch, tmp_path)

    name = "new_api"
    call_main(monkeypatch, tmp_path, name, "--api")

    assert_api(path=tmp_path / name, app_config_name="NewApiConfig")

    # Ensure that new api got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_api.apps.NewApiConfig"')


def test_creating_multiple_apps(monkeypatch, tmp_path):
    """Create multiple apps in an existing classic project."""

    _create_project(monkeypatch, tmp_path)

    # Create a new api named "new_api1"
    name = "new_api1"
    call_main(monkeypatch, tmp_path, name, "--api")

    assert_app(path=tmp_path / name, app_config_name="NewApi1Config")

    # Create another new api named "new_api2"
    name = "new_api2"
    call_main(monkeypatch, tmp_path, name, "--api")

    assert_app(path=tmp_path / "new_api2", app_config_name="NewApi2Config")

    # Ensure that new api got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_api1.apps.NewApi1Config"')
    assert_file(tmp_path / "config/settings.py", '"new_api2.apps.NewApi2Config"')


def test_minimal_fails(monkeypatch, tmp_path):
    """Check that creating a minimal app fails if there is an existing project."""

    _create_project(monkeypatch, tmp_path)

    with patch("django_new.cli.stderr") as mock_stderr:
        with pytest.raises(SystemExit) as excinfo:
            call_main(monkeypatch, tmp_path, "new_minimal_project", "--minimal")

        assert excinfo.value.code == 1

        mock_stderr.assert_called_once()


def test_web(monkeypatch, tmp_path):
    """Create a website in an existing classic project."""

    _create_project(monkeypatch, tmp_path)

    name = "new_web"
    call_main(monkeypatch, tmp_path, name, "--web")

    assert_web(path=tmp_path / name, app_name=name, app_config_name="NewWebConfig")

    # Ensure that new website got added to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_web.apps.NewWebConfig"')

    # Ensure static directories got created
    assert_folder(tmp_path / "static/css")
    assert_folder(tmp_path / "static/js")
    assert_folder(tmp_path / "static/img")


def test_worker(monkeypatch, tmp_path):
    """Create a worker in an existing classic project."""

    _create_project(monkeypatch, tmp_path)

    name = "new_worker"
    call_main(monkeypatch, tmp_path, name, "--worker")

    assert_worker(path=tmp_path / name, app_config_name="NewWorkerConfig")

    # Ensure that new worker got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_worker.apps.NewWorkerConfig"')
