from django_new.transformer import Runner
from django_new.transformer.transformations import WhitenoiseTransformation


def test_install(tmp_path):
    # Create some minimal files
    (tmp_path / "pyproject.toml").write_text("""
[project]
dependencies = []
""")

    (tmp_path / "settings.py").write_text("""
INSTALLED_APPS = []
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware"]
STORAGES = {}
""")

    runner = Runner(path=tmp_path, dry_run=True)

    migration = WhitenoiseTransformation(root_path=tmp_path)
    operations = runner.install(migration)

    assert operations
    assert len(operations) == 4

    runner = Runner(path=tmp_path, dry_run=False)
    runner.install(migration)

    expected = """
[project]
dependencies = ["whitenoise==6.6.0"]
"""
    actual = (tmp_path / "pyproject.toml").read_text()
    assert expected.strip() == actual.strip()

    expected = """
INSTALLED_APPS = ["whitenoise.runserver_nostatic"]
MIDDLEWARE = ["django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware"]
STORAGES = {'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
"""

    actual = (tmp_path / "settings.py").read_text()
    assert expected.strip() == actual.strip()
