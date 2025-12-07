from typer.testing import CliRunner

from django_new.cli import typer_app as app

runner = CliRunner()


def test_install_whitenoise(tmp_path):
    name = "new_project"
    result = runner.invoke(app, [name, str(tmp_path), "--project"])
    assert result.exit_code == 0

    # Verify whitenoise was not installed
    pyproject = tmp_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text()

    assert "whitenoise" not in content

    # Verify markdown file was created
    docs_dir = tmp_path / "django_new" / "md"
    assert docs_dir.exists()
    assert len(list(docs_dir.glob("*.md"))) == 1

    # Now run the install command
    result = runner.invoke(app, [str(tmp_path), "--install=whitenoise"])
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
    assert len(list(docs_dir.glob("*.md"))) == 2
