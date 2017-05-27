from collections import namedtuple

from marvin.runner.runner import Runner
from marvin.data import YAMLDataProvider, JSONDataProvider, NullDataProvider

from tests import resource as r


def build_options(**kwargs):
    options = namedtuple('Options', kwargs.keys())
    return options(**kwargs)


def test_suite_generation():
    options = build_options(tests_path=r('runner/scenario1'), with_tags=[], without_tags=[], config=None)
    collected = [(t.__name__, d.__class__, d.setup_data().get('name')) for (t, d) in Runner(options)._suite.tests()]

    assert ("VerifySomething", YAMLDataProvider, "verify_something.data1.yaml") in collected
    assert ("VerifySomething", JSONDataProvider, "verify_something.json") in collected
    assert ("AnotherCase", NullDataProvider, None) in collected
    assert len(collected) == 3


def test_tags_filtering():
    options = build_options(tests_path=r('runner/scenario1'), config=None,
                            with_tags=["tag1", "tag404"],
                            without_tags=[])
    collected = [(t.__name__, d.__class__, d.setup_data().get('name')) for (t, d) in Runner(options)._suite.tests()]

    assert ("VerifySomething", YAMLDataProvider, "verify_something.data1.yaml") in collected
    assert ("VerifySomething", JSONDataProvider, "verify_something.json") in collected
    assert len(collected) == 2

    options = build_options(tests_path=r('runner/scenario1'), config=None,
                            with_tags=["tag2"],
                            without_tags=["tag1"])
    collected = [(t.__name__, d.__class__, d.setup_data().get('name')) for (t, d) in Runner(options)._suite.tests()]
    assert ("AnotherCase", NullDataProvider, None) in collected
    assert len(collected) == 1


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
