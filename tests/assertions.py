import logging
from pathlib import Path

from tests.utils import print_directory_structure

logger = logging.getLogger(__name__)


def assert_file(path: Path, *contents):
    assert path.is_file()

    for content in contents:
        file_text = path.read_text()
        logger.debug(f"{path} file text: {file_text}")
        assert content in file_text

    return path


def assert_file_missing(path: Path):
    assert not path.exists()


def assert_base_project(path: Path, name: str):
    print_directory_structure(path)

    assert path.is_dir()

    assert assert_file(path / "manage.py")
    assert assert_file(path / "pyproject.toml", f'name = "{name}"', "Django>=5")
    assert assert_file(path / "README.md", f"# {name}")
    assert assert_file(path / ".gitignore")
    assert assert_file(path / ".env")


def assert_project(path: Path, name: str):
    assert_base_project(path=path, name=name)

    assert (path / "config").is_dir()
    assert assert_file(path / "config/__init__.py")
    assert assert_file(path / "config/asgi.py")
    assert assert_file(path / "config/settings.py")
    assert assert_file(path / "config/urls.py")
    assert assert_file(path / "config/wsgi.py")


def assert_base_app(path: Path, app_config_name: str):
    print_directory_structure(path)

    assert path.is_dir()

    assert_file(path / "apps.py", f"class {app_config_name}(AppConfig):")
    assert_file(path / "models.py")

    assert_file_missing(path / "tests.py")


def assert_app(path: Path, app_config_name: str):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "views.py")
    assert_file(path / "urls.py")


def assert_api(path: Path, app_config_name: str = "ApiConfig"):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "views.py")
    assert_file(path / "urls.py")


def assert_web(path: Path, app_config_name: str = "WebConfig"):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "views.py")
    assert_file(path / "urls.py")


def assert_worker(path: Path, app_config_name: str = "WorkerConfig"):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "tasks.py")

    # Ensure that regular app does not get created with views, urls
    assert_file_missing(path / "views.py")
    assert_file_missing(path / "urls.py")
