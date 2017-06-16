import os
from marvin.data.data_provider import DataProvider


class FileDataProvider(DataProvider):
    """
    Base abstract class for file system based data providers
    """

    def __init__(self, *args, **kargs):
        super(FileDataProvider, self).__init__(*args, **kargs)
        with open(self._source_id, "r") as file_handle:
            self._data = self.load_obj(file_handle)

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

    def meta(self):
        return self._data.get('meta', {})

    def setup_data(self):
        return self._data.get('setup', {})

    # GENERATOR
    def iteration_data(self):
        for it_data in self._data.get('iterations', []):
            yield it_data

    def tear_down_data(self):
        return self._data.get('tear_down', {})
