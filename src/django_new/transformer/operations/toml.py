from pathlib import Path
from typing import Any

import tomlkit

from django_new.transformer.operations import Operation


class TomlOperation(Operation):
    """Base class for all TOML operations"""

    def can_handle(self, path: Path) -> bool:
        return path.suffix == ".toml"


class AddKeyValue(TomlOperation):
    """Add a key-value pair to a TOML file"""

    def __init__(self, name: str, key: str, value: Any):
        self.name = name
        self.key = key
        self.value = value

    def description(self) -> str:
        return f"Add {self.key} = {self.value!r} to [{self.name}]"

    def apply(self, content: str) -> str:
        """Add a key-value pair to TOML"""

        doc = tomlkit.parse(content)

        # Navigate to the table
        keys = self.name.split(".")
        current = doc

        for key in keys:
            if key not in current:
                current[key] = {}

            current = current[key]

        # Add the value
        current[self.key] = self.value

        return tomlkit.dumps(doc)


class RemoveKey(TomlOperation):
    """Remove a key from a TOML file"""

    def __init__(self, table_path: str, key: str):
        self.table_path = table_path
        self.key = key

    def description(self) -> str:
        return f"Remove {self.key} from [{self.table_path}]"

    def apply(self, content: str) -> str:
        """Remove a key from TOML"""

        doc = tomlkit.parse(content)

        # Navigate to the table
        keys = self.table_path.split(".")
        current = doc

        for key in keys:
            if key not in current:
                raise ValueError(f"Table path '{self.table_path}' not found")

            current = current[key]

        # Remove the key
        if self.key not in current:
            raise ValueError(f"Key '{self.key}' not found in '{self.table_path}'")

        del current[self.key]

        return tomlkit.dumps(doc)


class AppendToList(TomlOperation):
    """Append a value to a list in a TOML file.

    The key can be a simple key (e.g., "dependencies") or use dot notation
    to specify nested tables (e.g., "project.dependencies").
    """

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value
        self._name_parts = name.split(".")
        self._list_key = self._name_parts[-1]
        self._table_name = ".".join(self._name_parts[:-1]) if len(self._name_parts) > 1 else ""

    def description(self) -> str:
        return f"Append {self.value!r} to {self.name}"

    def apply(self, content: str) -> str:
        doc = tomlkit.parse(content)
        current = doc

        # Navigate to the parent table if needed
        if self._table_name:
            for key in self._table_name.split("."):
                if key not in current:
                    current[key] = tomlkit.table()
                current = current[key]

        # Handle the list operation
        if self._list_key not in current:
            current[self._list_key] = tomlkit.array([self.value])
        else:
            if not isinstance(current[self._list_key], list | tomlkit.items.Array):
                raise ValueError(f"Cannot append to '{self._list_key}': target is not a list")
            current[self._list_key].append(self.value)

        return tomlkit.dumps(doc)
