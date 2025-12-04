from django_new.transformer import Runner, Transformation
from django_new.transformer.operations import python, toml


class WhitenoiseTransformation(Transformation):
    """Install and configure whitenoise for Django"""

    def forwards(self):
        # Add package to pyproject.toml
        self.modify_file("pyproject.toml", toml.AppendToList(name="project.dependencies", value="whitenoise==6.6.0"))

        # Add to INSTALLED_APPS
        self.modify_file(
            "settings.py",
            python.AppendToList(name="INSTALLED_APPS", value="'whitenoise.runserver_nostatic'", position=0),
        )

        # Add middleware
        self.modify_file(
            "settings.py",
            python.AppendToList(name="MIDDLEWARE", value="'whitenoise.middleware.WhiteNoiseMiddleware'", position=1),
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
    (tmp_path / "pyproject.toml").write_text("[project]\ndependencies = []\n\n")
    (tmp_path / "settings.py").write_text("INSTALLED_APPS = []\nMIDDLEWARE = []\n")

    runner = Runner(path=tmp_path, dry_run=True)

    migration = WhitenoiseTransformation(root_path=tmp_path)
    operations = runner.install(migration)

    assert operations
    assert len(operations) == 3

    runner = Runner(path=tmp_path, dry_run=False)
    runner.install(migration)

    expected = '[project]\ndependencies = ["whitenoise==6.6.0"]\n\n'
    actual = (tmp_path / "pyproject.toml").read_text()
    assert expected == actual

    expected = "INSTALLED_APPS = ['whitenoise.runserver_nostatic']\nMIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware']\n"
    actual = (tmp_path / "settings.py").read_text()
    assert expected == actual
