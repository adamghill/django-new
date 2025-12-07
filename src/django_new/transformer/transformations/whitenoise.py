from packaging.requirements import Requirement

from django_new.transformer import Transformation
from django_new.transformer.operations import python, toml


class WhitenoiseTransformation(Transformation):
    """Add whitenoise to a Django project"""

    def forwards(self):
        # Determine settings.py path
        settings_path = self.get_settings_file()

        # Add package to pyproject.toml dependencies
        dependencies = self.get_variable("pyproject.toml", "project.dependencies")

        for dependency in dependencies:
            req = Requirement(dependency)

            if req.name == "whitenoise":
                raise AssertionError("Whitenoise already installed")

        self.modify_file("pyproject.toml", toml.AppendToList(name="project.dependencies", value="whitenoise==6.6.0"))

        # Add whitenoise.runserver_nostatic to INSTALLED_APPS
        installed_apps = self.get_variable(settings_path, "INSTALLED_APPS")

        for app in installed_apps:
            if app == "whitenoise.runserver_nostatic":
                raise AssertionError("whitenoise.runserver_nostatic already installed")

        self.modify_file(
            settings_path,
            python.AppendToList(name="INSTALLED_APPS", value='"whitenoise.runserver_nostatic"', position=-1),
        )

        # Add whitenoise.middleware.WhiteNoiseMiddleware to MIDDLEWARE
        middlewares = self.get_variable(settings_path, "MIDDLEWARE")

        for middleware in middlewares:
            if middleware == "whitenoise.middleware.WhiteNoiseMiddleware":
                raise AssertionError("whitenoise.middleware.WhiteNoiseMiddleware already installed")

        self.modify_file(
            settings_path,
            python.AppendToList(
                name="MIDDLEWARE",
                value='"whitenoise.middleware.WhiteNoiseMiddleware"',
                after='"django.middleware.security.SecurityMiddleware"',
            ),
        )

        # Configure static files storage
        try:
            storages = self.get_variable(settings_path, "STORAGES")
        except ValueError:
            storages = {}

        for storage in storages:
            if storage == "whitenoise.storage.CompressedManifestStaticFilesStorage":
                raise AssertionError("whitenoise.storage.CompressedManifestStaticFilesStorage already installed")

        self.modify_file(
            settings_path,
            python.AssignVariable(
                name="STORAGES",
                value={
                    "staticfiles": {
                        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
                    },
                },
            ),
        )

    def backwards(self):
        # Determine settings.py path
        settings_path = self.get_settings_file()

        # Remove from INSTALLED_APPS
        self.modify_file(
            settings_path, python.RemoveFromList(list_name="INSTALLED_APPS", value="'whitenoise.runserver_nostatic'")
        )

        # Remove middleware
        self.modify_file(
            settings_path,
            python.RemoveFromList(list_name="MIDDLEWARE", value="'whitenoise.middleware.WhiteNoiseMiddleware'"),
        )

        # Reset STORAGES.staticfiles to empty dict
        self.modify_file(
            settings_path,
            python.AssignVariable(
                name="STORAGES",
                value={
                    "staticfiles": {},
                },
            ),
        )

        # Remove from pyproject.toml dependencies
        self.modify_file("pyproject.toml", toml.RemoveFromList(name="project.dependencies", value="whitenoise==6.6.0"))
