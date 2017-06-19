
class DataProvider(object):
    """
    Interface to be implemented by any data provider.
    """

    def __init__(self, source_id):
        """
        All data provider's should support instantiation from one given argument representing
        the source of the data to be fetched.
        E.g. for file-based data source (e.g. JSon, XML, YML, etc) the data source id might be
        the path of the file. For a DB provider, it might be a record id
        """
        self._source_id = source_id

    @classmethod
    def handles(cls, source_id):
        """Returns true if this data provider supports loading the give data source id"""
        raise NotImplementedError("Method must be redefined in %s" % cls.__name__)

    def meta(self):
        """
        Returns a dictionary with meta information for the test. Keys might include:
            * name: overrides the test case name
            * description: overrides the test case description
            * tags: extends the test case tag set
        """
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    def setup_data(self):
        """Returns a python object with the data to be passed to the 'setup' block of the Test Script"""
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    def iteration_data(self):
        """Returns python object's as a list or generator for each of the iterations"""
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    def tear_down_data(self):
        """Returns a python object with the data to be passed to the 'tear_down' block of the Test Script"""
        raise NotImplementedError("Method must be redefined %s" % self.__class__.__name__)
