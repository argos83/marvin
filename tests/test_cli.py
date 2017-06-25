import re
from marvin.runner import cli

from tests import resource as r
from tests import CaptureOutput


def test_arg_parse():
    options = cli.parse(['my_tests/', '--config', 'config.yaml',
                         '--tags', 'tag1', 'tag2', '--no-tags', 'tag3', 'tag4'])

    assert options.tests_path == 'my_tests/'
    assert options.with_tags == ['tag1', 'tag2']
    assert options.without_tags == ['tag3', 'tag4']
    assert options.config == 'config.yaml'


def test_runner_invocation_ok():
    exit_code = []
    cli.main(exit_fn=lambda code: exit_code.append(code),
             args=[r('runner/scenario1'), '--tags', 'pass'])
    assert exit_code == [0]


def test_runner_invocation_error():
    exit_code = []
    cli.main(exit_fn=lambda code: exit_code.append(code),
             args=[r('runner/scenario1'), '--tags', 'fail'])
    assert exit_code == [1]


def test_version():
    with CaptureOutput() as output:
        cli.main(args=['--version'])
    assert len(output) == 3
    assert re.match(r"^Marvin: \d+\.\d+\.\d+(?:\-.+)?", output[0]) is not None
    assert re.match(r"^Python: .+",  output[1]) is not None
    assert re.match(r"^Platform: .+", output[2]) is not None
