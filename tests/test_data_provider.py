import pytest

from marvin.data import DataProviderRegistry, DataProvider, FileDataProvider
from tests import resource as r


def test_default_data_providers():
    assert DataProviderRegistry.supported_file_extensions() == {'yaml', 'yml', 'json'}


def test_yaml_data_provider():
    data = DataProviderRegistry.data_provider_for(r('data/example.yaml'))
    assert data.meta() == {'name': 'Test Name', 'description': 'very descriptive', 'tags': ['bunch', 'of', 'tags']}
    assert data.setup_data() == {'a_list': [1, 2], 'foo': 'bar'}
    iterations = [d for d in data.iteration_data()]
    assert iterations == [{'arg1': 'iteration 1', 'arg2': True}, {'arg1': 'iteration 2', 'arg2': False}]
    assert data.tear_down_data() == {'foo': 'baz'}


def test_json_data_provider():
    data = DataProviderRegistry.data_provider_for(r('data/example.json'))
    assert data.setup_data() == {'a_list': [1, 2], 'foo': 'bar'}
    iterations = [d for d in data.iteration_data()]
    assert iterations == [{'arg1': 'iteration 1', 'arg2': True}, {'arg1': 'iteration 2', 'arg2': False}]
    assert data.tear_down_data() == {'foo': 'baz'}


def test_null_data_provider():
    data = DataProviderRegistry.data_provider_for(None)
    assert data.meta() == {}
    assert data.setup_data() == {}
    iterations = [d for d in data.iteration_data()]
    assert iterations == [{}]
    assert data.tear_down_data() == {}


def test_unimplemented_data_provider():
    class DummyDataProvider(DataProvider):
        pass

    with pytest.raises(NotImplementedError):
        DummyDataProvider.handles("a_file.md")

    dummy = DummyDataProvider("a_file.md")

    with pytest.raises(NotImplementedError):
        dummy.meta()

    with pytest.raises(NotImplementedError):
        dummy.setup_data()

    with pytest.raises(NotImplementedError):
        dummy.iteration_data()

    with pytest.raises(NotImplementedError):
        dummy.tear_down_data()


def test_unimplemented_file_data_provider():
    class DummyFileDataProvider(FileDataProvider):
        pass

    assert DummyFileDataProvider.handles(None) is False

    with pytest.raises(NotImplementedError):
        DummyFileDataProvider.handles(r('data/example.json'))

    with pytest.raises(NotImplementedError):
        DummyFileDataProvider(r('data/example.json'))
