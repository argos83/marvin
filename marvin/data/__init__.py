from marvin.data.data_provider import DataProvider
from marvin.data.data_provider_registry import DataProviderRegistry
from marvin.data.file_data_provider import FileDataProvider
from marvin.data.data_providers.yaml_data_provider import YAMLDataProvider
from marvin.data.data_providers.null_data_provider import NullDataProvider

__all__ = ['DataProvider', 'FileDataProvider', 'DataProviderRegistry']

DataProviderRegistry.register(YAMLDataProvider, NullDataProvider)
