from unittest.mock import patch

import pytest

from tests.assertions import (
    assert_api,
    assert_app,
    assert_file_missing,
    assert_folder,
    assert_project,
    assert_web,
    assert_worker,
)
from tests.utils import call_main


def test(monkeypatch, tmp_path):
    """Create an app with a project"""

    name = "new_app"
    call_main(monkeypatch, tmp_path, name)

    assert_project(path=tmp_path, name=name)
    assert_app(path=tmp_path / name, app_config_name="NewAppConfig")


def test_project(monkeypatch, tmp_path):
    """Create a project without an app"""

    name = "new_project"
    call_main(monkeypatch, tmp_path, name, "--project")

    assert_project(path=tmp_path, name=name)
    assert_file_missing(tmp_path / name / "apps.py")
    assert_file_missing(tmp_path / name / "models.py")


def test_app(monkeypatch, tmp_path):
    """Create an app without a project"""

    name = "new_app"
    call_main(monkeypatch, tmp_path, name, "--app")

    assert_app(path=tmp_path / name, app_config_name="NewAppConfig")
    assert_file_missing(tmp_path / "manage.py")
    assert_file_missing(tmp_path / "config" / "settings.py")


def test_api(monkeypatch, tmp_path):
    """Create an api with a project"""

    name = "new_api"
    call_main(monkeypatch, tmp_path, name, "--api")

    assert_project(path=tmp_path, name=name)
    assert_api(path=tmp_path / "api")


def test_web(monkeypatch, tmp_path):
    """Create a website with a project"""

    name = "new_web"
    call_main(monkeypatch, tmp_path, name, "--web")

    assert_project(path=tmp_path, name=name)
    assert_folder(tmp_path / "static/css")
    assert_folder(tmp_path / "static/js")
    assert_folder(tmp_path / "static/img")
    assert_web(path=tmp_path / "web")


def test_worker(monkeypatch, tmp_path):
    """Create a worker with a project"""

    name = "new_worker"
    call_main(monkeypatch, tmp_path, name, "--worker")

    assert_project(path=tmp_path, name=name)
    assert_worker(path=tmp_path / "worker")


def test_duplicate(monkeypatch, tmp_path):
    """Check that creating a duplicate app fails.

    The first call will make a new project named "new_api1" with an app named 'api'.
    The second call will fail because 'api' is passed in as the name and it already exists.
    """

    name = "new_api"
    call_main(monkeypatch, tmp_path, name, "--api")

    assert_project(path=tmp_path, name=name)
    assert_api(path=tmp_path / "api")

    with patch("django_new.cli.stderr") as mock_stderr:
        with pytest.raises(SystemExit) as excinfo:
            name = "api"
            call_main(monkeypatch, tmp_path, name)

        assert excinfo.value.code == 1

        mock_stderr.assert_called_once()
