from marvin import TestScript


class CheckSomething(TestScript):
    """Doesn't do much really"""
    NAME = "Some Test"
    TAGS = ["codeTag1", "codeTag2"]

    def run(self, data):
        pass
