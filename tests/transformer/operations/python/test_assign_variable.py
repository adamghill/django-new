from django_new.transformer.operations import python


def test_assign_string():
    content = "VAR = 'old'"
    op = python.AssignVariable(name="VAR", value="'new'")
    new_content = op.apply(content)
    assert new_content.strip() == "VAR = 'new'"


def test_assign_dict():
    content = "VAR = {}"
    op = python.AssignVariable(name="VAR", value={"key": "value"})
    new_content = op.apply(content)
    assert new_content.strip() == "VAR = {'key': 'value'}"


def test_assign_list():
    content = "VAR = []"
    op = python.AssignVariable(name="VAR", value=[1, 2, 3])
    new_content = op.apply(content)
    assert new_content.strip() == "VAR = [1, 2, 3]"


def test_assign_int():
    content = "VAR = 0"
    op = python.AssignVariable(name="VAR", value=42)
    new_content = op.apply(content)
    assert new_content.strip() == "VAR = 42"


def test_assign_bool():
    content = "VAR = False"
    op = python.AssignVariable(name="VAR", value=True)
    new_content = op.apply(content)
    assert new_content.strip() == "VAR = True"


def test_assign_existing_variable():
    content = "EXISTING = 'old'"
    op = python.AssignVariable(name="EXISTING", value="'new'")
    new_content = op.apply(content)
    assert new_content.strip() == "EXISTING = 'new'"


def test_assign_new_variable():
    content = "OTHER = 'val'"
    op = python.AssignVariable(name="NEW_VAR", value="'created'")
    new_content = op.apply(content)
    assert "NEW_VAR = 'created'" in new_content
    assert "OTHER = 'val'" in new_content
