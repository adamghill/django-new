import pytest

from django_new.transformer import Transformation
from django_new.transformer.operations.python import AppendToList
from django_new.transformer.operations.toml import AddKeyValue


class ConcreteTransformation(Transformation):
    """Concrete implementation for testing"""

    def forwards(self):
        """Test implementation of forwards"""
        operation = AppendToList(name="TEST_LIST", value='"test_value"')
        self.modify_file(path="test_file.py", operation=operation)

    def backwards(self):
        """Test implementation of backwards"""
        pass


def test_transformation_init(fake_fs, temp_path):
    """Test Transformation initialization"""
    transformation = ConcreteTransformation(root_path=temp_path)

    assert transformation.root_path == temp_path
    assert transformation._changes == []


def test_assert_path_is_valid_with_nonexistent_file(fake_fs, temp_path):
    """Test that assert_path_is_valid raises error for nonexistent file"""
    transformation = ConcreteTransformation(root_path=temp_path)
    nonexistent = temp_path / "nonexistent.py"

    with pytest.raises(FileNotFoundError, match="File not found"):
        transformation.assert_path_is_valid(nonexistent)


def test_assert_path_outside_root_raises_error(fake_fs, temp_path):
    """Test that assert_path_is_valid raises error for paths outside root"""
    transformation = ConcreteTransformation(root_path=temp_path)

    # Create a file outside the root
    outside_path = temp_path.parent / "outside.py"
    outside_path.write_text("# test")

    with pytest.raises(ValueError, match="not within the project root"):
        transformation.assert_path_is_valid(outside_path)


def test_modify_file_with_invalid_operation(fake_fs, temp_path):
    """Test that modify_file raises error for invalid operation"""
    transformation = ConcreteTransformation(root_path=temp_path)

    # Create a Python file
    test_file = temp_path / "test.py"
    test_file.write_text("TEST_LIST = []")

    # Try to apply a TOML operation to a Python file
    toml_operation = AddKeyValue(name="section", key="key", value="value")

    with pytest.raises(ValueError, match="cannot handle file"):
        transformation.modify_file(path=test_file, operation=toml_operation)


def test_rollback_changes_after_error(fake_fs, temp_path):
    """Test that rollback_changes restores original content"""
    transformation = ConcreteTransformation(root_path=temp_path)

    # Create a test file
    test_file = temp_path / "test.py"
    original_content = "TEST_LIST = []"
    test_file.write_text(original_content)

    # Apply an operation
    operation = AppendToList(name="TEST_LIST", value='"item1"')
    transformation.modify_file(path=test_file, operation=operation)

    # Verify file was modified
    modified_content = test_file.read_text()
    assert modified_content != original_content
    assert '"item1"' in modified_content

    # Rollback changes
    transformation.rollback_changes()

    # Verify file was restored
    restored_content = test_file.read_text()
    assert restored_content == original_content


def test_rollback_changes_multiple_files(fake_fs, temp_path):
    """Test rollback with multiple file modifications"""
    transformation = ConcreteTransformation(root_path=temp_path)

    # Create multiple test files
    file1 = temp_path / "file1.py"
    file2 = temp_path / "file2.py"
    original1 = "LIST1 = []"
    original2 = "LIST2 = []"
    file1.write_text(original1)
    file2.write_text(original2)

    # Modify both files
    transformation.modify_file(path=file1, operation=AppendToList(name="LIST1", value='"a"'))
    transformation.modify_file(path=file2, operation=AppendToList(name="LIST2", value='"b"'))

    # Verify both were modified
    assert file1.read_text() != original1
    assert file2.read_text() != original2

    # Rollback
    transformation.rollback_changes()

    # Verify both were restored
    assert file1.read_text() == original1
    assert file2.read_text() == original2


def test_rollback_clears_changes_list(fake_fs, temp_path):
    """Test that rollback clears the changes list"""
    transformation = ConcreteTransformation(root_path=temp_path)

    test_file = temp_path / "test.py"
    test_file.write_text("TEST_LIST = []")

    transformation.modify_file(path=test_file, operation=AppendToList(name="TEST_LIST", value='"x"'))

    assert len(transformation._changes) == 1

    transformation.rollback_changes()

    assert len(transformation._changes) == 0


def test_modify_file_with_relative_path(fake_fs, temp_path):
    """Test modify_file resolves relative paths correctly"""
    transformation = ConcreteTransformation(root_path=temp_path)

    # Create a file
    test_file = temp_path / "test.py"
    test_file.write_text("TEST_LIST = []")

    # Modify using relative path
    transformation.modify_file(path="test.py", operation=AppendToList(name="TEST_LIST", value='"item"'))

    # Verify it was modified
    content = test_file.read_text()
    assert '"item"' in content
