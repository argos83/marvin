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

    def tags_match(self, tags):
        """
        To be redefined by specific Suite implementations that want to support tests/data/iteration filtering by tags
        :param tags: [set] a set of tags
        :return: [boolean] True if the set of tags match the filter implementation, False otherwise
        """
        return True
