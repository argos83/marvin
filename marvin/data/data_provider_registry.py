
class DataProviderRegistry(object):
    """
    Keeps track of the available DataProvider classes
    """

    DATA_PROVIDERS = []

    @classmethod
    def register(cls, *data_provider_classes):
        for dp in data_provider_classes:
            if dp not in cls.DATA_PROVIDERS:
                cls.DATA_PROVIDERS.insert(0, dp)

    @classmethod
    def data_provider_for(cls, source_id):
        return next((dp(source_id) for dp in cls.DATA_PROVIDERS if dp.handles(source_id)), None)

    @classmethod
    def supported_file_extensions(cls):
        return set(ext
                   for dp in cls.DATA_PROVIDERS if hasattr(dp, 'supported_extensions')
                   for ext in dp.supported_extensions())
