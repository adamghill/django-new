from pathlib import Path
from typing import Any

import libcst as cst

from django_new.transformer.operations import Operation


class PythonOperation(Operation):
    """Base class for all Python operations"""

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".py"


class AppendToList(PythonOperation):
    """Append a value to a Python list, supporting nested class traversal"""

    class AddToListTransformer(cst.CSTTransformer):
        """CST transformer to add items to a list, supporting nested class traversal"""

        def __init__(self, name: str, value: str, position: int | None, after: str | None):
            self.name = name.split(".")
            self.value = value
            self.position = position
            self.after = after
            self.found = False
            self.current_name = []

        def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:  # noqa: N802
            self.current_name.append(node.name.value)

            return True

        def leave_ClassDef(self, _: cst.ClassDef, updated_node: cst.CSTNode) -> cst.CSTNode:  # noqa: N802
            if self.current_name:
                self.current_name.pop()

            return updated_node

        def leave_Assign(self, _: cst.Assign, updated_node: cst.Assign) -> cst.CSTNode:  # noqa: N802
            # Skip if we're not at the right path depth
            # For nested attributes, the path length should match the current name parts
            # e.g., for 'Settings.INSTALLED_APPS', we want to match when current_name is ['Settings']
            if len(self.current_name) != len(self.name) - 1:
                return updated_node

            # Check if this is an assignment to our target list
            target = updated_node.targets[0].target

            # Handle direct name access (e.g., INSTALLED_APPS)
            if isinstance(target, cst.Name):
                target_name = target.value

                # If we're in a class context, we need to check if the class name matches
                if self.current_name and self.current_name[0] == self.name[0]:
                    if target_name == self.name[-1] and isinstance(updated_node.value, cst.List):
                        self.found = True

                        return self._add_to_list_node(updated_node)

                # If not in a class context, just match the name
                elif len(self.name) == 1 and target_name == self.name[0] and isinstance(updated_node.value, cst.List):
                    self.found = True

                    return self._add_to_list_node(updated_node)

            # Handle nested attributes (e.g., Settings.INSTALLED_APPS)
            elif isinstance(target, cst.Attribute):
                # Check if the attribute path matches our target
                attr_parts = []
                node = target

                while isinstance(node, cst.Attribute):
                    attr_parts.append(node.attr.value)
                    node = node.value

                if isinstance(node, cst.Name):
                    attr_parts.append(node.value)
                    attr_parts.reverse()  # Reverse to get the correct order

                    # Check if the full path matches our target
                    if ".".join(attr_parts) == ".".join(self.name) and isinstance(updated_node.value, cst.List):
                        self.found = True
                        return self._add_to_list_node(updated_node)

            return updated_node

        def _add_to_list_node(self, node):
            """Add the value to the list node"""

            # Parse the value as a CST element
            value_node = cst.parse_expression(self.value)
            new_element = cst.Element(value=value_node)

            # Get existing elements
            elements = list(node.value.elements)

            # Insert at position
            if self.after:
                insert_pos = 0
                for i, element in enumerate(elements):
                    # Get the code for the element value to compare
                    element_code = cst.Module([]).code_for_node(element.value).strip()
                    if element_code == self.after:
                        insert_pos = i + 1
                        break
                elements.insert(insert_pos, new_element)
            elif self.position is None:
                elements.append(new_element)
            elif self.position < 0:
                # Negative indexing
                insert_pos = len(elements) + self.position + 1
                elements.insert(max(0, insert_pos), new_element)
            else:
                elements.insert(min(self.position, len(elements)), new_element)

            # Return updated node
            return node.with_changes(value=node.value.with_changes(elements=elements))

    def __init__(self, name: str, value: str, position: int | None = None, after: str | None = None):
        self.name = name
        self.value = value
        self.position = position
        self.after = after

    def description(self) -> str:
        if self.after:
            return f"Append {self.value} to {self.name} after {self.after}"
        pos = f" at position {self.position}" if self.position is not None else ""

        return f"Append {self.value} to {self.name}{pos}"

    def apply(self, content: str) -> str:
        """Add a value to a list in Python code"""

        tree = cst.parse_module(content)
        transformer = self.AddToListTransformer(self.name, self.value, self.position, self.after)
        modified_tree = tree.visit(transformer)

        if not transformer.found:
            raise ValueError(f"List '{self.name}' not found in file")

        return modified_tree.code


class RemoveFromList(PythonOperation):
    """Remove a value from a Python list"""

    class RemoveFromListTransformer(cst.CSTTransformer):
        """CST transformer to remove items from a list"""

        def __init__(self, list_name: str, value: str):
            self.list_name = list_name.split(".")
            self.value = value
            self.found = False
            self.removed = False
            self.current_name = []

        def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:  # noqa: N802
            self.current_name.append(node.name.value)

            return True

        def leave_ClassDef(self, _: cst.ClassDef, updated_node: cst.CSTNode) -> cst.CSTNode:  # noqa: N802
            if self.current_name:
                self.current_name.pop()

            return updated_node

        def leave_Assign(self, _: cst.Assign, updated_node: cst.Assign) -> cst.CSTNode:  # noqa: N802
            # Skip if we're not at the right path depth
            if len(self.current_name) != len(self.list_name) - 1:
                return updated_node

            target = updated_node.targets[0].target

            # Handle direct name access
            if isinstance(target, cst.Name):
                target_name = target.value

                if self.current_name and self.current_name[0] == self.list_name[0]:
                    if target_name == self.list_name[-1] and isinstance(updated_node.value, cst.List):
                        self.found = True

                        return self._remove_from_list_node(updated_node)
                elif (
                    len(self.list_name) == 1
                    and target_name == self.list_name[0]
                    and isinstance(updated_node.value, cst.List)
                ):
                    self.found = True

                    return self._remove_from_list_node(updated_node)

            # Handle nested attributes
            elif isinstance(target, cst.Attribute):
                attr_parts = []
                node = target

                while isinstance(node, cst.Attribute):
                    attr_parts.append(node.attr.value)
                    node = node.value

                if isinstance(node, cst.Name):
                    attr_parts.append(node.value)
                    attr_parts.reverse()

                    if ".".join(attr_parts) == ".".join(self.list_name) and isinstance(updated_node.value, cst.List):
                        self.found = True

                        return self._remove_from_list_node(updated_node)

            return updated_node

        def _remove_from_list_node(self, node):
            """Remove the value from the list node"""

            # Parse the value to compare
            target_value = cst.parse_expression(self.value)

            # Filter out matching elements
            new_elements = []

            for element in node.value.elements:
                if not element.value.deep_equals(target_value):
                    new_elements.append(element)
                else:
                    self.removed = True

            return node.with_changes(value=node.value.with_changes(elements=new_elements))

    def __init__(self, list_name: str, value: str):
        self.list_name = list_name
        self.value = value

    def description(self) -> str:
        return f"Remove {self.value} from {self.list_name}"

    def apply(self, content: str) -> str:
        """Remove a value from a list in Python code"""

        tree = cst.parse_module(content)
        transformer = self.RemoveFromListTransformer(self.list_name, self.value)
        modified_tree = tree.visit(transformer)

        if not transformer.found:
            raise ValueError(f"List '{self.list_name}' not found in file")
        if not transformer.removed:
            raise ValueError(f"Value {self.value} not found in '{self.list_name}'")

        return modified_tree.code


class GetVariable(PythonOperation):
    """Get the value of a Python variable"""

    class GetVariableVisitor(cst.CSTVisitor):
        """CST visitor to extract variable values"""

        def __init__(self, name: str):
            self.name = name.split(".")
            self.value = None
            self.current_name = []

        def visit_ClassDef(self, node: cst.ClassDef) -> bool | None:  # noqa: N802
            self.current_name.append(node.name.value)
            return True

        def leave_ClassDef(self, node: cst.ClassDef) -> None:  # noqa: N802, ARG002
            if self.current_name:
                self.current_name.pop()

        def visit_Assign(self, node: cst.Assign) -> bool | None:  # noqa: N802
            # Skip if we're not at the right path depth
            if len(self.current_name) != len(self.name) - 1:
                return True

            target = node.targets[0].target

            # Handle direct name access (e.g., STATIC_ROOT)
            if isinstance(target, cst.Name):
                target_name = target.value

                # If we're in a class context, check if the class name matches
                if self.current_name and self.current_name[0] == self.name[0]:
                    if target_name == self.name[-1]:
                        self.value = cst.Module([]).code_for_node(node.value)
                        return False  # Stop visiting once found

                # If not in a class context, just match the name
                elif len(self.name) == 1 and target_name == self.name[0]:
                    self.value = cst.Module([]).code_for_node(node.value)
                    return False  # Stop visiting once found

            # Handle nested attributes (e.g., Settings.STATIC_ROOT)
            elif isinstance(target, cst.Attribute):
                attr_parts = []
                attr_node = target

                while isinstance(attr_node, cst.Attribute):
                    attr_parts.append(attr_node.attr.value)
                    attr_node = attr_node.value

                if isinstance(attr_node, cst.Name):
                    attr_parts.append(attr_node.value)
                    attr_parts.reverse()

                    # Check if the full path matches our target
                    if ".".join(attr_parts) == ".".join(self.name):
                        self.value = cst.Module([]).code_for_node(node.value)
                        return False  # Stop visiting once found

            return True

    def __init__(self, name: str):
        self.name = name

    def description(self) -> str:
        return f"Get value of {self.name}"

    def apply(self, content: str) -> str:
        """Get the value of a variable from Python code"""

        tree = cst.parse_module(content)
        visitor = self.GetVariableVisitor(self.name)
        tree.visit(visitor)

        if visitor.value is None:
            raise ValueError(f"Variable '{self.name}' not found in file")

        return visitor.value


class AssignVariable(PythonOperation):
    """Assign a value to a variable, creating it if it doesn't exist"""

    class AssignVariableTransformer(cst.CSTTransformer):
        def __init__(self, name: str, value: str):
            self.name = name
            self.value = value
            self.found = False

        def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.CSTNode:  # noqa: N802, ARG002
            # Check if this assignment matches our target
            for target in updated_node.targets:
                if isinstance(target.target, cst.Name) and target.target.value == self.name:
                    self.found = True
                    # Replace value
                    value_node = cst.parse_expression(self.value)
                    return updated_node.with_changes(value=value_node)
            return updated_node

    def __init__(self, name: str, value: str | Any):
        self.name = name
        if not isinstance(value, str):
            value = repr(value)
        self.value = value

    def description(self) -> str:
        return f"Assign {self.value} to {self.name}"

    def apply(self, content: str) -> str:
        tree = cst.parse_module(content)
        transformer = self.AssignVariableTransformer(self.name, self.value)
        modified_tree = tree.visit(transformer)

        if not transformer.found:
            # Append to end of module
            assign_stmt = cst.parse_statement(f"{self.name} = {self.value}")
            # Add to body
            new_body = list(modified_tree.body)
            new_body.append(assign_stmt)
            modified_tree = modified_tree.with_changes(body=new_body)

        return modified_tree.code
