import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from django_new.cli import typer_app as app
from tests.assertions import (
    assert_api,
    assert_app,
    assert_data,
    assert_file,
    assert_file_missing,
    assert_folder,
    assert_project,
    assert_web,
    assert_worker,
)

runner = CliRunner(catch_exceptions=False)


def test(fake_fs, temp_path):
    """Create an app with a project"""

    name = "new_app"

    result = runner.invoke(app, [name, str(temp_path)])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_app(path=temp_path / name, app_name=name, app_config_name="NewAppConfig")


def test_with_dash_yes(fake_fs, temp_path):
    """Create an app with a project that includes dashes"""

    name = "new-app"
    result = runner.invoke(app, [name, str(temp_path)], input="y\n")

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_app(path=temp_path / "new_app", app_name="new_app", app_config_name="NewAppConfig")


def test_with_dash_default(fake_fs, temp_path):
    """Create an app with a project that includes dashes"""

    name = "new-app"
    result = runner.invoke(app, [name, str(temp_path)], input="\n")

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_app(path=temp_path / "new_app", app_name="new_app", app_config_name="NewAppConfig")


def test_with_dash_no(fake_fs, temp_path):
    """Create an app with a project that includes dashes"""

    name = "new-app"
    result = runner.invoke(app, [name, str(temp_path)], input="n\n")

    assert result.exit_code == 0

    assert_file_missing(temp_path / "manage.py")


def test_project(fake_fs, temp_path):
    """Create a project without an app"""

    name = "new_project"
    result = runner.invoke(app, [name, str(temp_path), "--project"])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_file_missing(temp_path / name / "apps.py")
    assert_file_missing(temp_path / name / "models.py")


def test_app(fake_fs, temp_path):
    """Create an app without a project"""

    name = "new_app"
    result = runner.invoke(app, [name, str(temp_path), "--app"])

    assert result.exit_code == 0

    assert_app(path=temp_path / name, app_name=name, app_config_name="NewAppConfig")
    assert_file_missing(temp_path / "manage.py")
    assert_file_missing(temp_path / "config" / "settings.py")


def test_api(fake_fs, temp_path):
    """Create an api with a project"""

    name = "new_api"
    result = runner.invoke(app, [name, str(temp_path), "--api"])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_api(path=temp_path / "api")


def test_web(fake_fs, temp_path):
    """Create a website with a project"""

    name = "new_web"
    result = runner.invoke(app, [name, str(temp_path), "--web"])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_folder(temp_path / "static/css")
    assert_folder(temp_path / "static/js")
    assert_folder(temp_path / "static/img")
    assert_web(path=temp_path / "web")


def test_data(fake_fs, temp_path):
    """Create a data with a project"""

    name = "new_data"
    result = runner.invoke(app, [name, str(temp_path), "--data"])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_data(path=temp_path / "data")


def test_worker(fake_fs, temp_path):
    """Create a worker with a project"""

    name = "new_worker"
    result = runner.invoke(app, [name, str(temp_path), "--worker"])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_worker(path=temp_path / "worker")


def test_template_folder(temp_path):
    """Use temp_path instead of fake_fs because because of the relative path."""

    name = "new_project"
    result = runner.invoke(app, [name, str(temp_path), "--template=tests/django-template"])

    assert result.exit_code == 0

    assert_file(temp_path / "manage.py")


def test_starter_folder(temp_path):
    """Use temp_path instead of fake_fs because because of the relative path."""

    name = "new_project"
    result = runner.invoke(app, [name, str(temp_path), "--starter=tests/django-template"])

    assert result.exit_code == 0

    assert_file(temp_path / "manage.py")


def test_template_zip_file(temp_path):
    """Create a project with a template zip file.

    Use subprocess to run the CLI to completely isolate the test from
    pyfakefs state leakage from other tests.
    """

    if False:
        # Create zip file from template directory
        import os  # noqa: PLC0415
        import zipfile  # noqa: PLC0415

        with zipfile.ZipFile("tests/django-template.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk("tests/django-template"):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname("tests/django-template"))
                    zipf.write(file_path, arcname=arcname)

    # Ensure the zip file exists (it should be in the repo)
    assert Path("tests/django-template.zip").exists()

    name = "new_project"

    # Run the CLI command in a subprocess to isolate the test from pyfakefs state leakage from other tests.
    cmd = [sys.executable, "-m", "django_new.cli", name, str(temp_path), "--template=tests/django-template.zip"]
    result = subprocess.run(cmd, capture_output=True, text=True)  # noqa: S603

    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

    assert result.returncode == 0

    assert_file(temp_path / "manage.py")


def test_duplicate(fake_fs, temp_path):
    """Check that creating a duplicate app fails.

    The first call will make a new project named "new_api" with an app named 'api'.
    The second call will fail because 'api' is passed in as the name and it already exists.
    """

    name = "new_api"
    result = runner.invoke(app, [name, str(temp_path), "--api"])

    assert result.exit_code == 0

    assert_project(path=temp_path, name=name)
    assert_api(path=temp_path / "api")

    with patch("django_new.cli.stderr") as mock_stderr:
        result = runner.invoke(app, ["api", str(temp_path)])

        assert result.exit_code == 1
        mock_stderr.assert_called()


def test_python_version_arg(fake_fs, temp_path):
    """Create a project with a custom Python version"""
    name = "python_version_test"
    python_version = ">=3.9,<3.12"

    result = runner.invoke(app, [name, str(temp_path), f"--python={python_version}"])

    assert result.exit_code == 0
    assert_project(path=temp_path, name=name)

    # Verify the Python version in pyproject.toml
    pyproject_path = temp_path / "pyproject.toml"
    assert pyproject_path.exists()

    pyproject_content = pyproject_path.read_text()
    assert f'requires-python = "{python_version}"' in pyproject_content


def test_django_version_arg(fake_fs, temp_path):
    """Create a project with a custom Django version"""
    name = "django_version_test"
    django_version = ">=4.2,<5.0"

    result = runner.invoke(app, [name, str(temp_path), f"--django={django_version}"])

    assert result.exit_code == 0
    assert_project(path=temp_path, name=name, django_version=django_version)

    # Verify the Django version in pyproject.toml
    pyproject_path = temp_path / "pyproject.toml"
    assert pyproject_path.exists()

    pyproject_content = pyproject_path.read_text()
    assert f'"Django{django_version}"' in pyproject_content
