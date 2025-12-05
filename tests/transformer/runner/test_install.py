from django_new.transformer import Runner, Transformation
from django_new.transformer.operations import python, toml


class WhitenoiseTransformation(Transformation):
    """Install and configure whitenoise for Django"""

    def forwards(self):
        # TODO: Check for whitenoise in dependencies and skip if it's already there
        # Add package to pyproject.toml
        self.modify_file("pyproject.toml", toml.AppendToList(name="project.dependencies", value="whitenoise==6.6.0"))

        # TODO: Check for whitenoise in INSTALLED_APPS and skip if it's already there
        # Add to INSTALLED_APPS
        self.modify_file(
            "settings.py",
            python.AppendToList(name="INSTALLED_APPS", value="'whitenoise.runserver_nostatic'", position=0),
        )

        # TODO: Check for whitenoise in MIDDLEWARE and skip if it's already there
        # Add middleware
        self.modify_file(
            "settings.py",
            python.AppendToList(
                name="MIDDLEWARE",
                value="'whitenoise.middleware.WhiteNoiseMiddleware'",
                after="'django.middleware.security.SecurityMiddleware'",
            ),
        )

        # TODO: Check for whitenoise in STORAGES and skip if it's already there
        # Configure static files storage
        self.modify_file(
            "settings.py",
            python.AssignVariable(
                name="STORAGES",
                value={
                    "staticfiles": {
                        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                    },
                },
            ),
        )

    # def backwards(self):
    #     # Remove from pyproject.toml
    #     self.modify_file("pyproject.toml", toml.RemoveKey("dependencies", "whitenoise"))

    #     # Remove from INSTALLED_APPS
    #     self.modify_file(
    #         "settings.py", python.RemoveFromList(name="INSTALLED_APPS", value="'whitenoise.runserver_nostatic'")
    #     )

    #     # Remove middleware
    #     self.modify_file(
    #         "settings.py",
    #         python.RemoveFromList(name="MIDDLEWARE", value="'whitenoise.middleware.WhiteNoiseMiddleware'"),
    #     )


def test_install(tmp_path):
    # Create some minimal files
    (tmp_path / "pyproject.toml").write_text("""
[project]
dependencies = []""")

    (tmp_path / "settings.py").write_text("""
INSTALLED_APPS = []
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware']
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
INSTALLED_APPS = ['whitenoise.runserver_nostatic']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'whitenoise.middleware.WhiteNoiseMiddleware']
STORAGES = {'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
"""

    actual = (tmp_path / "settings.py").read_text()
    assert expected.strip() == actual.strip()
