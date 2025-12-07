from django_new.transformer import Transformation


class DummyTransformation(Transformation):
    def forwards(self):
        # Create a dummy file
        (self.root_path / "dummy.txt").write_text("dummy")

    def backwards(self):
        (self.root_path / "dummy.txt").unlink(missing_ok=True)
