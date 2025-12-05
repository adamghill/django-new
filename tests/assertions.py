import logging
from pathlib import Path

from tests.utils import print_directory_structure

logger = logging.getLogger(__name__)


def assert_folder(path: Path):
    assert path.is_dir()


def assert_file(path: Path, *contents):
    assert path.is_file()

    for content in contents:
        file_text = path.read_text()
        logger.debug(f"{path} file text: {file_text}")
        assert content in file_text


def assert_file_missing(path: Path):
    assert not path.exists()


def assert_base_project(path: Path, name: str, django_version: str = ">=5"):
    print_directory_structure(path)

    assert_folder(path)

    assert_file(path / "manage.py")
    assert_file(path / "pyproject.toml", f'name = "{name}"', f"Django{django_version}")
    assert_file(path / "README.md", f"# {name}")
    assert_file(path / ".gitignore")
    assert_file(path / ".env")


def assert_project(path: Path, name: str, django_version: str = ">=5"):
    assert_base_project(path=path, name=name, django_version=django_version)

    assert_folder(path / "tests")

    project_folder = path / "config"
    assert_folder(project_folder)

    assert_file(project_folder / "__init__.py")
    assert_file(project_folder / "asgi.py")
    assert_file(project_folder / "settings.py")
    assert_file(project_folder / "urls.py")
    assert_file(project_folder / "wsgi.py")


def assert_base_app(path: Path, app_config_name: str):
    print_directory_structure(path)

    assert_folder(path)

    assert_file(path / "apps.py", f"class {app_config_name}(AppConfig):")
    assert_file(path / "models.py")

    assert_file_missing(path / "tests.py")


def assert_app(path: Path, app_name: str, app_config_name: str):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "views.py")
    assert_test_directory(project_path=path.parent, app_name=app_name)


def assert_api(path: Path, app_config_name: str = "ApiConfig"):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "views.py")
    assert_file(path / "urls.py")


def assert_web(path: Path, app_name="web", app_config_name: str = "WebConfig"):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "views.py")
    assert_file(path / "urls.py")
    assert_file(path / "templatetags" / "__init__.py")
    assert_file(path / "templates" / app_name / "index.html")


def assert_worker(path: Path, app_config_name: str = "WorkerConfig"):
    assert_base_app(path=path, app_config_name=app_config_name)
    assert_file(path / "tasks.py")

    # Ensure that regular app does not get created with views, urls
    assert_file_missing(path / "views.py")
    assert_file_missing(path / "urls.py")


def assert_test_directory(project_path: Path, app_name: str):
    """Assert that a test directory exists for the given app.

    Args:
        project_path: Path to the project root
        app_name: Name of the app to check test directory for
    """
    test_dir = project_path / "tests" / app_name
    assert test_dir.is_dir(), f"Test directory not found at {test_dir}"
    assert (test_dir / "__init__.py").is_file(), f"__init__.py not found in {test_dir}"
