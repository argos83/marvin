from marvin import TestScript


class AnotherCase(TestScript):
    """Checks something else somewhere else"""
    NAME = "Another case that fails"
    TAGS = ["tag2", "tag3", "fail"]

    def setup(self, data):
        pass

    def run(self, data):
        5/0

    def tear_down(self, _data):
        pass
