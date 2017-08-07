import pytest

from marvin.data import DataProviderRegistry, DataProvider, FileDataProvider
from tests import resource as r


def test_default_data_providers():
    assert DataProviderRegistry.supported_file_extensions() == {'yaml', 'yml', 'json'}


def test_yaml_data_provider():
    data = DataProviderRegistry.data_provider_for(r('data/example.yaml'))
    assert data.name == 'Test Name'
    assert data.description == 'very descriptive'
    assert data.tags == {'bunch', 'of', 'tags'}
    assert data.setup_data == {'a_list': [1, 2], 'foo': 'bar'}
    iterations = [(i.name, i.description, i.tags, i.data) for i in data.iterations]
    assert iterations == [
        ('First iteration', None, None,
         {'arg1': 'iteration 1', 'arg2': True}),
        ('Second Iteration', 'iteration description', {'regression'},
         {'arg1': 'iteration 2', 'arg2': False})
    ]
    assert data.tear_down_data == {'foo': 'baz'}


def test_json_data_provider():
    data = DataProviderRegistry.data_provider_for(r('data/example.json'))
    assert data.name == 'Test Name'
    assert data.description == 'very descriptive'
    assert data.tags == {'bunch', 'of', 'tags'}
    assert data.setup_data == {'a_list': [1, 2], 'foo': 'bar'}
    iterations = [(i.name, i.description, i.tags, i.data) for i in data.iterations]
    assert iterations == [
        (None, None, None, {'arg1': 'iteration 1', 'arg2': True}),
        (None, None, None, {'arg1': 'iteration 2', 'arg2': False})
    ]
    assert data.tear_down_data == {'foo': 'baz'}


def test_load_empty_yaml():
    data = DataProviderRegistry.data_provider_for(r('data/empty.yaml'))
    assert data.name is None
    assert data.description is None
    assert data.tags is None
    assert data.setup_data is None
    iterations = [i for i in data.iterations]
    assert iterations == []
    assert data.tear_down_data is None


def test_null_data_provider():
    data = DataProviderRegistry.data_provider_for(None)
    assert data.name is None
    assert data.description is None
    assert data.tags is None
    assert data.setup_data is None
    iterations = [i for i in data.iterations]
    assert len(iterations) == 1
    iteration = iterations[0]
    assert iteration.name is None
    assert iteration.description is None
    assert iteration.tags is None
    assert iteration.data is None
    assert data.tear_down_data is None


def test_unimplemented_data_provider():
    class DummyDataProvider(DataProvider):
        pass

    with pytest.raises(NotImplementedError):
        DummyDataProvider.handles("a_file.md")

    dummy = DummyDataProvider("a_file.md")

    with pytest.raises(NotImplementedError):
        dummy.name

    with pytest.raises(NotImplementedError):
        dummy.description

    with pytest.raises(NotImplementedError):
        dummy.tags

    with pytest.raises(NotImplementedError):
        dummy.setup_data

    with pytest.raises(NotImplementedError):
        dummy.iterations

    with pytest.raises(NotImplementedError):
        dummy.tear_down_data


def test_unimplemented_file_data_provider():
    class DummyFileDataProvider(FileDataProvider):
        pass

    assert DummyFileDataProvider.handles(None) is False

    with pytest.raises(NotImplementedError):
        DummyFileDataProvider.handles(r('data/example.json'))

    with pytest.raises(NotImplementedError):
        DummyFileDataProvider(r('data/example.json'))


def test_iterations_no_data_key_and_unexpected_keys():
    data = DataProviderRegistry.data_provider_for(r('data/iterations_unexpected_keys.yaml'))
    assert data.name == 'Test unexpected keys'
    assert data.description == 'Should not fail'
    assert data.tags == {'bunch', 'of', 'tags'}
    assert data.setup_data == {'a_list': [1, 2]}
    iterations = [(i.name, i.description, i.tags, i.data) for i in data.iterations]
    assert iterations == [
        ('First iteration', None, None, None)
    ]
    assert data.tear_down_data == {'foo': 'baz'}
