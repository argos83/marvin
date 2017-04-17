"""Null Data Provider"""
from marvin.data.data_provider import DataProvider


class NullDataProvider(DataProvider):
    """
    Default DataDriven data provider that yields a single iteration with no data.
    For cases where test scripts aren't implemented as a data-driven (more like unit test frameworks)
    """

    def __init__(self):
        super(NullDataProvider, self).__init__(None)

    def setup_data(self):
        return {}

    def iteration_data(self):
        return [{}]

    def tear_down_data(self):
        return {}
