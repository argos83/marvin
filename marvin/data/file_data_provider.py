import os
from marvin.data import DataProvider, IterationData


class FileDataProvider(DataProvider):
    """
    Base abstract class for file system based data providers
    """

    def __init__(self, *args, **kargs):
        super(FileDataProvider, self).__init__(*args, **kargs)
        with open(self._source_id, "r") as file_handle:
            self._data = self.load_obj(file_handle) or {}

    @classmethod
    def supported_extensions(cls):
        raise NotImplementedError("Method must be redefined in %s" % cls.__name__)

    @classmethod
    def load_obj(cls, file_handle):
        raise NotImplementedError("Method must be redefined in %s" % cls.__name__)

    @classmethod
    def handles(cls, source_id):
        if not source_id:
            return False
        _, ext = os.path.splitext(source_id)
        return ext and ext[1:].lower() in cls.supported_extensions()

    # Overrides
    @property
    def name(self):
        return self._data.get('name')

    # Overrides
    @property
    def description(self):
        return self._data.get('description')

    # Overrides
    @property
    def tags(self):
        tags = self._data.get('tags')
        return set(tags) if tags else None

    # Overrides
    @property
    def setup_data(self):
        return self._data.get('setup_data')

    # Overrides
    @property
    def iterations(self):
        for it_data in self._data.get('iterations', []):
            yield IterationData(**it_data)

    # Overrides
    @property
    def tear_down_data(self):
        return self._data.get('tear_down_data')
