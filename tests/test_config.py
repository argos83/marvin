from tests import resource as r


def test_config_load_yaml(config):
    config.load(r('config/dummy_config.yml'))
    print(config.dummy_config)
    assert config.dummy_config['a_nested']['a_list'] == ['test1', 'test2', 'test3']


def test_config_load_json(config):
    config.load(r('config/some_json.json'))
    assert config.some_json['important_setting'] == 42


def test_config_load_multiple_files(config):
    config.load(r('config/dummy_config.yml'), r('config/some_json.json'))
    assert config.dummy_config['some_key'] == 'with a value'
    assert config.some_json['important_setting'] == 42


def test_load_in_different_namespace(config):
    config.load_into(r('config/some_json.json'), namespace='test')
    assert config.test['important_setting'] == 42


def test_settings_merge_if_same_basename(config):
    config.load(r('config/dummy_config.yml'))
    config.load(r('config/config_override/dummy_config.yaml'))
    assert config.dummy_config['some_key'] == 'with a value'
    assert config.dummy_config['extra_key'] == 'bar'
    assert config.dummy_config['a_test'] is None


def test_config_load_value(config):
    config.set('answer', 42)
    assert config.answer == 42
