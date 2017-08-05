class IterationData(object):
    """
    Models an iteration data and meta data.
    """

    def __init__(self, data=None, name=None, description=None, tags=None, **_kwargs):
        self._data = data
        self._name = name
        self._description = description
        self._tags = set(str(tag) for tag in tags) if tags else None

    @property
    def name(self):
        """
        iteration name
        :return: [None|String]
        """
        return self._name

    @property
    def description(self):
        """
        iteration description
        :return: [None|String]
        """
        return self._description

    @property
    def tags(self):
        """
        iteration tags
        :return: set
        """
        return self._tags

    @property
    def data(self):
        """
        iteration data
        :return: anything
        """
        return self._data
