from typer.testing import CliRunner

from django_new.cli import typer_app as app

runner = CliRunner()


def test_install_whitenoise(tmp_path):
    name = "new_project"
    result = runner.invoke(app, [name, str(tmp_path), "--web", "--install=whitenoise"])

    assert result.exit_code == 0

    # Verify whitenoise was installed
    pyproject = tmp_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text()

    assert "whitenoise" in content

    settings = tmp_path / "config" / "settings.py"
    assert settings.exists()
    settings_content = settings.read_text()
    assert "whitenoise.runserver_nostatic" in settings_content
    assert "whitenoise.middleware.WhiteNoiseMiddleware" in settings_content

    # Verify markdown file was created
    docs_dir = tmp_path / "django_new" / "md"
    assert docs_dir.exists()
    assert len(list(docs_dir.glob("*.md"))) == 1


def test_install_multiple_transformations(tmp_path):
    name = "new_project"

    # Run command with multiple install flags
    # We use "whitenoise" (short name) and "tests.transformations.dummy" (dotted path)
    result = runner.invoke(
        app, [name, str(tmp_path), "--web", "--install=whitenoise", "--install=tests.transformations.dummy"]
    )

    assert result.exit_code == 0

    # Verify whitenoise installed
    pyproject = tmp_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text()
    assert "whitenoise" in content

    # Verify dummy installed
    dummy_file = tmp_path / "dummy.txt"
    assert dummy_file.exists()
    assert dummy_file.read_text() == "dummy"


def test_create_project_with_install_failure(tmp_path):
    name = "new_project"

    # Run command with a transformation that fails
    result = runner.invoke(app, [name, str(tmp_path), "--web", "--install=tests.transformations.error"])

    assert result.exit_code == 1
    assert "Failed to install tests.transformations.error" in result.stderr
