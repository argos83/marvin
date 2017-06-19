"""Null Data Provider"""
from marvin.data.data_provider import DataProvider


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

    def meta(self):
        return {}

    def setup_data(self):
        return {}

    def iteration_data(self):
        return [{}]

    def tear_down_data(self):
        return {}
