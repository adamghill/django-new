from unittest.mock import patch

from typer.testing import CliRunner

from django_new.cli import typer_app as app
from tests.assertions import (
    assert_api,
    assert_app,
    assert_file,
    assert_folder,
    assert_project,
    assert_web,
    assert_worker,
)

runner = CliRunner()


def _create_project(tmp_path):
    name = "bare_project"
    result = runner.invoke(app, [name, str(tmp_path), "--project"])

    assert result.exit_code == 0


def test(tmp_path):
    """Create an app in an existing classic project."""

    _create_project(tmp_path)

    name = "new_app"
    result = runner.invoke(app, [name, str(tmp_path)])

    assert result.exit_code == 0

    assert_app(path=tmp_path / name, app_name=name, app_config_name="NewAppConfig")

    # Ensure that new app got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", f'"{name}.apps.NewAppConfig"')


def test_app(tmp_path):
    """Create an app in an existing classic project."""

    _create_project(tmp_path)

    name = "new_app"
    result = runner.invoke(app, [name, str(tmp_path), "--app"])

    assert result.exit_code == 0

    assert_app(path=tmp_path / name, app_name=name, app_config_name="NewAppConfig")

    # Ensure that new app got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", f'"{name}.apps.NewAppConfig"')


def test_api(tmp_path):
    """Create an api in an existing classic project."""

    _create_project(tmp_path)

    name = "new_api"
    result = runner.invoke(app, [name, str(tmp_path), "--api"])

    assert result.exit_code == 0

    assert_api(path=tmp_path / name, app_config_name="NewApiConfig")

    # Ensure that new api got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_api.apps.NewApiConfig"')


def test_creating_multiple_apps(tmp_path):
    """Create multiple apps in an existing classic project."""

    _create_project(tmp_path)

    # Create a new api named "new_api1"
    name = "new_api1"
    runner.invoke(app, ["--api", name, str(tmp_path)])

    assert_app(path=tmp_path / name, app_name=name, app_config_name="NewApi1Config")

    # Create another new api named "new_api2"
    name = "new_api2"
    runner.invoke(app, ["--api", name, str(tmp_path)])

    assert_app(path=tmp_path / "new_api2", app_name=name, app_config_name="NewApi2Config")

    # Ensure that new api got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_api1.apps.NewApi1Config"')
    assert_file(tmp_path / "config/settings.py", '"new_api2.apps.NewApi2Config"')


def test_web(tmp_path):
    """Create a website in an existing classic project."""

    _create_project(tmp_path)

    name = "new_web"
    result = runner.invoke(app, [name, str(tmp_path), "--web"])

    assert result.exit_code == 0

    assert_web(path=tmp_path / name, app_name=name, app_config_name="NewWebConfig")

    # Ensure that new website got added to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_web.apps.NewWebConfig"')

    # Ensure static directories got created
    assert_folder(tmp_path / "static/css")
    assert_folder(tmp_path / "static/js")
    assert_folder(tmp_path / "static/img")


def test_worker(tmp_path):
    """Create a worker in an existing classic project."""

    _create_project(tmp_path)

    name = "new_worker"
    result = runner.invoke(app, [name, str(tmp_path), "--worker"])

    assert result.exit_code == 0

    assert_worker(path=tmp_path / name, app_config_name="NewWorkerConfig")

    # Ensure that new worker got add to existing project
    assert_project(path=tmp_path, name="bare_project")
    assert_file(tmp_path / "config/settings.py", '"new_worker.apps.NewWorkerConfig"')


def test_minimal_fails(tmp_path):
    """Check that creating a minimal app fails if there is an existing project."""

    _create_project(tmp_path)

    with patch("django_new.cli.stderr") as mock_stderr:
        result = runner.invoke(app, ["new_minimal_project", str(tmp_path), "--minimal"])

        assert result.exit_code == 1
        mock_stderr.assert_called_once()


def test_template_fails(tmp_path):
    """Check that creating a template app fails if there is an existing project."""

    _create_project(tmp_path)

    with patch("django_new.cli.stderr") as mock_stderr:
        result = runner.invoke(
            app,
            ["new_minimal_project", str(tmp_path), "--template=tests/django-template"],
        )

        assert result.exit_code == 1
        mock_stderr.assert_called_once()
