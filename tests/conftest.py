import tempfile
from pathlib import Path

import _pytest.config
import _pytest.pathlib
import django
import pytest
from django.conf import settings

# Monkeypatch _pytest.pathlib.bestrelpath to avoid ValueError with pyfakefs
# Only needed when there is an error
original_bestrelpath = _pytest.pathlib.bestrelpath


def patched_bestrelpath(directory, base):
    try:
        return original_bestrelpath(directory, base)
    except ValueError:
        return str(directory)


_pytest.pathlib.bestrelpath = patched_bestrelpath
_pytest.config.bestrelpath = patched_bestrelpath


@pytest.fixture
def temp_path():
    tmp_dir = tempfile.TemporaryDirectory()

    yield Path(tmp_dir.name)


def pytest_addoption(parser):
    parser.addoption(
        "--real-fs", action="store_true", default=False, help="Use the real filesystem instead of pyfakefs"
    )


@pytest.fixture
def fake_fs(fs, request):
    """Configure pyfakefs to allow access to template files.

    This fixture extends the standard pyfakefs `fs` fixture to:
    1. Skip patching Django modules so management commands work
    2. Allow access to the real django_new package files (especially templates)
    3. Use the fake filesystem for test operations
    """

    if request.config.getoption("--real-fs"):
        fs.pause()

    # Get the project root directory (parent of tests/)
    project_root = Path(__file__).parent.parent

    # Add the Python installation directory so Django management commands work
    python_lib = project_root / ".venv" / "lib"
    fs.add_real_directory(
        str(python_lib),
        read_only=True,
    )

    # Allow access to the django_new package so templates can be read
    django_new_src = project_root / "src" / "django_new"
    fs.add_real_directory(
        str(django_new_src),
        read_only=True,
    )

    # Allow access to the tests directory so templates can be read
    tests_src = project_root / "tests"
    fs.add_real_directory(
        str(tests_src),
        read_only=True,
    )

    return fs


def pytest_configure():
    if not settings.configured:
        settings.configure(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.sites",
                "django.contrib.messages",
                "django.contrib.staticfiles",
            ],
            MIDDLEWARE=[
                "django.middleware.security.SecurityMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
        )
        django.setup()
