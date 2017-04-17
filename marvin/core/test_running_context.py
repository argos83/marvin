from marvin.core.context import Context


class TestRunningContext(object):
    """
    A Mix-In for contexts that are allowed to run tests.
    E.g. Suites can run tests
    """

    def __init__(self):
        assert isinstance(self, Context)

    def test(self, test_class):
        """Instantiates a new test with this as it's parent context"""
        # TODO: assert test_class is subclsas of TestScript
        return test_class(self)
