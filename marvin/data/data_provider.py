
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

    @property
    def name(self):
        """
        Overrides the test case name
        :return: [None|String]
        """
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    @property
    def description(self):
        """
        Overrides the test case description
        :return: [None|String]
        """
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    @property
    def tags(self):
        """
        Extends the test case tag set
        :return: [None|iterable[String]]
        """
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    @property
    def setup_data(self):
        """Returns a python object with the data to be passed to the 'setup' phase of the Test Script"""
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    @property
    def iterations(self):
        """
        Returns python object's as a list or generator for each of the iterations
        Each yielded item is an instance of marvin.data.IterationData:
        """
        raise NotImplementedError("Method must be redefined in %s" % self.__class__.__name__)

    @property
    def tear_down_data(self):
        """Returns a python object with the data to be passed to the 'tear_down' phase of the Test Script"""
        raise NotImplementedError("Method must be redefined %s" % self.__class__.__name__)
