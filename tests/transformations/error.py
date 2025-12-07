from django_new.transformer import Transformation


class ErrorTransformation(Transformation):
    def forwards(self):
        raise ValueError("Simulated failure")

    def backwards(self):
        pass
