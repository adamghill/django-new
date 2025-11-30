import tempfile
from pathlib import Path

from django_new.formatters.adder import add_to_list


def test_add_to_existing_list():
    expected = 'MY_LIST = [\n    "item1",\n    "item2",\n]\n'

    # Create a temporary file with a list
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        f.write('MY_LIST = [\n    "item1",\n]\n')
        temp_path = Path(f.name)

    try:
        # Add a new item to the list
        add_to_list(temp_path, "MY_LIST", "item2")

        # Read the modified file
        with open(temp_path) as f:
            content = f.read()

        assert expected == content
    finally:
        temp_path.unlink()


def test_add_to_empty_list():
    expected = 'MY_LIST = ["item1",]\n'

    # Create a temporary file with an empty list
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as f:
        f.write("MY_LIST = []\n")
        temp_path = Path(f.name)

    try:
        # Add a new item to the list
        add_to_list(temp_path, "MY_LIST", "item1")

        # Read the modified file
        with open(temp_path) as f:
            content = f.read()

        assert expected == content
    finally:
        temp_path.unlink()
