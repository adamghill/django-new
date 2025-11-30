from unittest.mock import patch

from typer.testing import CliRunner

from django_new.cli import app
from tests.assertions import (
    assert_api,
    assert_app,
    assert_file,
    assert_file_missing,
    assert_folder,
    assert_project,
    assert_web,
    assert_worker,
)

runner = CliRunner(catch_exceptions=False)


def test(tmp_path):
    """Create an app with a project"""

    name = "new_app"

    result = runner.invoke(app, [name, str(tmp_path)])

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_app(path=tmp_path / name, app_config_name="NewAppConfig")


def test_with_dash_yes(tmp_path):
    """Create an app with a project that includes dashes"""

    name = "new-app"
    result = runner.invoke(app, [name, str(tmp_path)], input="yes\n")

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_app(path=tmp_path / "new_app", app_config_name="NewAppConfig")


def test_with_dash_default(tmp_path):
    """Create an app with a project that includes dashes"""

    name = "new-app"
    result = runner.invoke(app, [name, str(tmp_path)], input="\n")

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_app(path=tmp_path / "new_app", app_config_name="NewAppConfig")


def test_with_dash_no(tmp_path):
    """Create an app with a project that includes dashes"""

    name = "new-app"
    result = runner.invoke(app, [name, str(tmp_path)], input="no\n")

    assert result.exit_code == 0

    assert_file_missing(tmp_path / "manage.py")


def test_project(tmp_path):
    """Create a project without an app"""

    name = "new_project"
    result = runner.invoke(app, [name, str(tmp_path), "--project"])

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_file_missing(tmp_path / name / "apps.py")
    assert_file_missing(tmp_path / name / "models.py")


def test_app(tmp_path):
    """Create an app without a project"""

    name = "new_app"
    result = runner.invoke(app, [name, str(tmp_path), "--app"])

    assert result.exit_code == 0

    assert_app(path=tmp_path / name, app_config_name="NewAppConfig")
    assert_file_missing(tmp_path / "manage.py")
    assert_file_missing(tmp_path / "config" / "settings.py")


def test_api(tmp_path):
    """Create an api with a project"""

    name = "new_api"
    result = runner.invoke(app, [name, str(tmp_path), "--api"])

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_api(path=tmp_path / "api")


def test_web(tmp_path):
    """Create a website with a project"""

    name = "new_web"
    result = runner.invoke(app, [name, str(tmp_path), "--web"])

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_folder(tmp_path / "static/css")
    assert_folder(tmp_path / "static/js")
    assert_folder(tmp_path / "static/img")
    assert_web(path=tmp_path / "web")


def test_worker(tmp_path):
    """Create a worker with a project"""

    name = "new_worker"
    result = runner.invoke(app, [name, str(tmp_path), "--worker"])

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_worker(path=tmp_path / "worker")


def test_template_folder(tmp_path):
    name = "new_project"
    result = runner.invoke(app, [name, str(tmp_path), "--template=tests/django-template"])

    assert result.exit_code == 0

    assert_file(tmp_path / "manage.py")


def test_template_zip_file(tmp_path):
    """Create a project with a template zip file"""

    if False:
        # Create zip file from template directory
        import os
        import zipfile

        with zipfile.ZipFile("tests/django-template.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk("tests/django-template"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname("tests/django-template"))
                    zipf.write(file_path, arcname=arcname)

    name = "new_project"
    result = runner.invoke(app, [name, str(tmp_path), "--template=tests/django-template.zip"])

    assert result.exit_code == 0

    assert_file(tmp_path / "manage.py")


def test_duplicate(tmp_path):
    """Check that creating a duplicate app fails.

    The first call will make a new project named "new_api" with an app named 'api'.
    The second call will fail because 'api' is passed in as the name and it already exists.
    """

    name = "new_api"
    result = runner.invoke(app, [name, str(tmp_path), "--api"])

    assert result.exit_code == 0

    assert_project(path=tmp_path, name=name)
    assert_api(path=tmp_path / "api")

    with patch("django_new.cli.stderr") as mock_stderr:
        result = runner.invoke(app, ["api", str(tmp_path)])

        assert result.exit_code == 1
        mock_stderr.assert_called()
