from typer.testing import CliRunner

from django_new.cli import typer_app as app

runner = CliRunner()


def test_install_whitenoise(fake_fs, temp_path):
    name = "new_project"
    result = runner.invoke(app, [name, str(temp_path), "--web", "--install=whitenoise"])

    assert result.exit_code == 0

    # Verify whitenoise was installed
    pyproject = temp_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text()

    assert "whitenoise" in content

    settings = temp_path / "config" / "settings.py"
    assert settings.exists()
    settings_content = settings.read_text()
    assert "whitenoise.runserver_nostatic" in settings_content
    assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings_content

    # Verify markdown file was created
    docs_dir = temp_path / "django_new" / "md"
    assert docs_dir.exists()
    assert len(list(docs_dir.glob("*.md"))) == 1


def test_install_multiple_transformations(fake_fs, temp_path):
    name = "new_project"

    # Run command with multiple install flags
    # We use "whitenoise" (short name) and "tests.transformations.dummy" (dotted path)
    result = runner.invoke(
        app, [name, str(temp_path), "--web", "--install=whitenoise", "--install=tests.transformations.dummy"]
    )

    assert result.exit_code == 0

    # Verify whitenoise installed
    pyproject = temp_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text()
    assert "whitenoise" in content

    # Verify dummy installed
    dummy_file = temp_path / "dummy.txt"
    assert dummy_file.exists()
    assert dummy_file.read_text() == "dummy"


def test_create_project_with_install_failure(fake_fs, temp_path):
    name = "new_project"

    # Run command with a transformation that fails
    result = runner.invoke(app, [name, str(temp_path), "--web", "--install=tests.transformations.error"])

    assert result.exit_code == 1
    assert "Failed to install tests.transformations.error" in result.stderr
