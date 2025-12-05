from django_new.transformer.transformations import WhitenoiseTransformation


def test_whitenoise_backwards_rollback(tmp_path):
    """Test that backwards function correctly rolls back all changes made by forwards"""
    # Create initial files
    original_pyproject = """[project]
name = "myproject"
dependencies = ["django>=4.2"]
"""
    original_settings = """INSTALLED_APPS = ['django.contrib.admin']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware']
STORAGES = {}
"""

    (tmp_path / "pyproject.toml").write_text(original_pyproject)
    (tmp_path / "settings.py").write_text(original_settings)

    # Apply forwards transformation
    transformation = WhitenoiseTransformation(root_path=tmp_path)
    transformation.forwards()

    # Verify changes were applied
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    settings_content = (tmp_path / "settings.py").read_text()

    assert "whitenoise==6.6.0" in pyproject_content
    assert "'whitenoise.runserver_nostatic'" in settings_content
    assert "'whitenoise.middleware.WhiteNoiseMiddleware'" in settings_content
    assert "whitenoise.storage.CompressedManifestStaticFilesStorage" in settings_content

    # Apply backwards transformation
    transformation.backwards()

    # Verify everything was rolled back
    pyproject_content = (tmp_path / "pyproject.toml").read_text()
    settings_content = (tmp_path / "settings.py").read_text()

    # Check pyproject.toml - whitenoise should be gone
    assert "whitenoise" not in pyproject_content.lower()
    assert "django>=4.2" in pyproject_content

    # Check settings.py - whitenoise elements should be gone
    assert "whitenoise.runserver_nostatic" not in settings_content
    assert "whitenoise.middleware.WhiteNoiseMiddleware" not in settings_content
    assert "whitenoise.storage.CompressedManifestStaticFilesStorage" not in settings_content

    # The original apps and middleware should still be there
    assert "'django.contrib.admin'" in settings_content
    assert "'django.middleware.security.SecurityMiddleware'" in settings_content
