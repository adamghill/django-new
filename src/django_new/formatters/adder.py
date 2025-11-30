from pathlib import Path
from typing import Any

import libcst as cst


class ListAdder(cst.CSTTransformer):
    def __init__(self, target_variable_name: str, new_list_element: Any):
        self.target_variable_name = target_variable_name
        self.new_list_element = new_list_element

    def leave_Assign(self, original_node, updated_node):  # noqa: ARG002, N802
        if (
            isinstance(updated_node.targets[0], cst.AssignTarget)
            and updated_node.targets[0].target.value == self.target_variable_name
        ):
            # Get the existing elements
            existing_elements = list(updated_node.value.elements)

            # Create new element - just copy the comma structure from the last element
            if existing_elements:
                # Remove trailing comma from last element and add it to new element
                last_element = existing_elements[-1]

                # Update the last element to have a trailing comma with newline
                updated_last = last_element.with_changes(
                    comma=cst.Comma(
                        whitespace_after=cst.ParenthesizedWhitespace(
                            first_line=cst.TrailingWhitespace(
                                whitespace=cst.SimpleWhitespace(""),
                                newline=cst.Newline("\n"),
                            ),
                            indent=True,
                            last_line=cst.SimpleWhitespace("    "),
                        )
                    )
                )

                # Ensure the string is properly quoted
                quoted_element = f'"{self.new_list_element}"'

                new_element = cst.Element(
                    value=cst.SimpleString(quoted_element),
                    comma=cst.Comma(whitespace_after=cst.SimpleWhitespace("")),
                )

                # Replace last element and add new one
                new_elements = [*existing_elements[:-1], updated_last, new_element]
            else:
                # If list is empty, just add the element with proper quoting
                quoted_element = f'"{self.new_list_element}"'

                new_element = cst.Element(
                    value=cst.SimpleString(quoted_element),
                    comma=cst.Comma(whitespace_after=cst.SimpleWhitespace("")),
                )
                new_elements = [new_element]

            # Create new list
            new_list = cst.List(
                lbracket=updated_node.value.lbracket,
                rbracket=updated_node.value.rbracket,
                elements=new_elements,
            )

            return updated_node.with_changes(value=new_list)

        return updated_node


def add_to_list(path: Path, target_variable_name: str, new_list_element: Any):
    code = path.read_text()

    tree = cst.parse_module(code)
    modified_tree = tree.visit(ListAdder(target_variable_name, new_list_element))
    path.write_text(modified_tree.code)
