"""Null Data Provider"""
from marvin.data import DataProvider, IterationData


class NullDataProvider(DataProvider):
    """
    Default DataDriven data provider that yields a single iteration with no data.
    For cases where test scripts aren't implemented as a data-driven (more like unit test frameworks)
    """

    @classmethod
    def handles(cls, source_id):
        return source_id is None

    def __init__(self, *_args):
        super(NullDataProvider, self).__init__(None)

    @property
    def name(self):
        return None

    @property
    def description(self):
        return None

    @property
    def tags(self):
        return None

    @property
    def setup_data(self):
        return None

    @property
    def iterations(self):
        return [IterationData()]

    @property
    def tear_down_data(self):
        return None
