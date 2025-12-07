import importlib
import inspect

from django_new.transformer import Transformation


def resolve_transformation(name: str) -> type[Transformation]:
    """
    Resolve a transformation class from a string.
    The string can be a short name (e.g. "whitenoise") which looks in
    django_new.transformer.transformations, or a dotted path.
    """

    module_path = name

    if "." not in name:
        module_path = f"django_new.transformer.transformations.{name}"

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not import transformation module '{name}'") from e

    # Find a class that inherits from Transformation
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Transformation) and obj is not Transformation:
            return obj

    raise ValueError(f"No Transformation class found in module '{module_path}'")
