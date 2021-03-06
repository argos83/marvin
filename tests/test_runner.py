import os
import copy
from collections import namedtuple

from marvin.report import EventType
from marvin.runner.runner import Runner
from marvin.runner.runtime_suite import default_config
from marvin.data import YAMLDataProvider, NullDataProvider

from tests import resource as r, env_var


def build_options(**kwargs):
    options = namedtuple('Options', kwargs.keys())
    return options(**kwargs)


def collect_iteration_names(options):
    iterations = []
    runner = Runner(options)
    runner._suite.publisher.subscribe(lambda e: iterations.append(e.iteration.name), EventType.TEST_ITERATION_STARTED)
    runner.run()
    return sorted(iterations)


def test_suite_generation():
    options = build_options(tests_path=r('runner/scenario1'), with_tags=[], without_tags=[], config=None)
    collected = [(t.__name__, d.__class__, (d.setup_data or {}).get('name'))
                 for (t, d) in Runner(options)._suite.tests()]

    assert ("VerifySomething", YAMLDataProvider, "verify_something.data1.yaml") in collected
    assert ("VerifySomething", YAMLDataProvider, "verify_something.json") in collected
    assert ("AnotherCase", NullDataProvider, None) in collected
    assert len(collected) == 3


def test_filtering_from_tags_in_code():
    options = build_options(tests_path=r('runner/scenario1'), config=None,
                            with_tags=["tag1", "tag404"],
                            without_tags=[])
    iterations = collect_iteration_names(options)
    assert iterations == ["json-iteration1", "json-iteration2", "yaml-iteration1", "yaml-iteration2"]

    options = build_options(tests_path=r('runner/scenario1'), config=None,
                            with_tags=["tag2"],
                            without_tags=["tag1"])
    iterations = collect_iteration_names(options)
    assert iterations == [None]  # AnotherCase with NullDataProvider


def test_filtering_from_tags_in_data():
    # No filters runs all
    options = build_options(tests_path=r('runner/scenario2'), config=None, with_tags=[], without_tags=[])
    iterations = collect_iteration_names(options)
    assert iterations == ['Iteration A', 'Iteration B', 'Iteration C', 'Iteration D']

    # matching whole data tag
    options = build_options(tests_path=r('runner/scenario2'), config=None, with_tags=['data1'], without_tags=[])
    iterations = collect_iteration_names(options)
    assert iterations == ['Iteration A', 'Iteration B']

    # skipping whole data tag
    options = build_options(tests_path=r('runner/scenario2'), config=None, with_tags=[], without_tags=['data1'])
    iterations = collect_iteration_names(options)
    assert iterations == ['Iteration C', 'Iteration D']

    # matching single iteration
    options = build_options(tests_path=r('runner/scenario2'), config=None, with_tags=['iterationA'], without_tags=[''])
    iterations = collect_iteration_names(options)
    assert iterations == ['Iteration A']

    # skipping single iteration
    options = build_options(tests_path=r('runner/scenario2'), config=None, with_tags=[], without_tags=['iterationB'])
    iterations = collect_iteration_names(options)
    assert iterations == ['Iteration A', 'Iteration C', 'Iteration D']

    # matching single iterations in multiple files
    options = build_options(tests_path=r('runner/scenario2'), config=None, with_tags=['regression'], without_tags=[])
    iterations = collect_iteration_names(options)
    assert iterations == ['Iteration A', 'Iteration C']


def test_loaded_configuration():
    expected_default = default_config()
    expected_from_file = default_config()
    expected_from_file.update({
        'tests_path': 'scenario1/',
        'filter': {'with_tags': ['include-this'], 'without_tags': ['exclude-this']},
        'some_setting': 'some value'
    })
    expected_file_with_override = copy.deepcopy(expected_from_file)
    expected_file_with_override['tests_path'] = 'another/path'

    options = build_options(config=None, tests_path=None, with_tags=None, without_tags=None)
    assert Runner(options)._suite.cfg.marvin == expected_default

    options = build_options(config=r('runner/marvin.yaml'), tests_path=None, with_tags=None, without_tags=None)
    assert Runner(options)._suite.cfg.marvin == expected_from_file

    with env_var('MARVIN_CONFIG', r('runner/marvin.yaml')):
        options = build_options(config=None, tests_path=None, with_tags=None, without_tags=None)
        assert Runner(options)._suite.cfg.marvin == expected_from_file

    options = build_options(config=r('runner/marvin.yaml'), tests_path='another/path',
                            with_tags=None, without_tags=None)
    assert Runner(options)._suite.cfg.marvin == expected_file_with_override


def test_hook_module_loaded():
    options = build_options(config=r('runner/marvin_hook_test.yaml'), tests_path=None, with_tags=None,
                            without_tags=None)

    assert os.environ.get('SOME_MARVIN_TEST') is None
    suite = Runner(options)._suite
    assert os.environ.get('SOME_MARVIN_TEST') == "%s - %s" % (id(suite.publisher), id(suite.cfg))


def test_env_settings_loaded():
    options = build_options(config=r('runner/marvin_env_test.yaml'), tests_path=None, with_tags=None,
                            without_tags=None)
    cfg = Runner(options)._suite.cfg
    assert cfg.service_x['url'] == 'http://dev.example.com'
    assert cfg.service_x['timeout'] == 42
    assert cfg.other['important'] == 'setting'

    with env_var('MARVIN_ENV', 'production'):
        options = build_options(config=r('runner/marvin_env_test.yaml'), tests_path=None, with_tags=None,
                                without_tags=None)
        cfg = Runner(options)._suite.cfg
        assert cfg.service_x['url'] == 'http://prod.example.com'
        assert cfg.service_x['timeout'] == 42
        assert cfg.other['important'] == 'setting'


def test_exit_code_success():
    options = build_options(tests_path=r('runner/scenario1'), config=None,
                            with_tags=["pass"], without_tags=[])

    code = Runner(options).run()
    assert code == 0


def test_exit_code_failure():
    options = build_options(tests_path=r('runner/scenario1'), config=None,
                            with_tags=["fail"], without_tags=[])

    code = Runner(options).run()
    assert code != 0
