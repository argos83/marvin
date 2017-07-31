from marvin import TestScript


class VerifySomething(TestScript):
    """Verifies something somewhere"""
    NAME = "Verify Something"
    TAGS = ["tag1", "tag2", "pass"]

    def setup(self, data):
        pass

    def run(self, data):
        pass

    def tear_down(self, _data):
        pass
