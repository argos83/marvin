
class DataProviderRegistry(object):
    """
    Keeps track of the available DataProvider classes
    """

    DATA_PROVIDERS = []

    @classmethod
    def register(cls, *data_provider_classes):
        for data_provider_class in data_provider_classes:
            if data_provider_class not in cls.DATA_PROVIDERS:
                cls.DATA_PROVIDERS.insert(0, data_provider_class)

    @classmethod
    def data_provider_for(cls, data_source_id):
        return next((data_provider_class(data_source_id)
                     for data_provider_class in cls.DATA_PROVIDERS
                     if data_provider_class.handles(data_source_id)), None)

    @classmethod
    def supported_file_extensions(cls):
        return set(ext
                   for dp in cls.DATA_PROVIDERS if hasattr(dp, 'supported_extensions')
                   for ext in dp.supported_extensions())
