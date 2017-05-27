from marvin import TestScript


class NotFoundTest(TestScript):
    """This should never be executed since it is in a '.directory'"""

    def setup(self, data):
        pass

    def run(self, data):
        pass

    def tear_down(self, _data):
        pass
