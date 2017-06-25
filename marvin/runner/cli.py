import sys
import argparse

import marvin
from marvin.runner.runner import Runner


def main(exit_fn=sys.exit, args=None):
    options = parse(args)
    if options.version:
        sys_info()
    else:
        exit_fn(Runner(options).run())


def parse(args):
    parser = argparse.ArgumentParser(description='Marvin test runner')
    parser.add_argument('tests_path', metavar='DIRECTORY', nargs='?', default=None,
                        help='root directory containing tests')
    parser.add_argument('--config', '-c', dest='config',
                        help='path to config file')
    parser.add_argument('--tags', nargs='*', dest='with_tags',
                        help='only run tests containing any of the given tags')
    parser.add_argument('--no-tags', nargs='*', dest='without_tags',
                        help='don\'t run tests containing any of the given tags')
    parser.add_argument('--version', action='store_true',
                        help='display Marvin version and exit')

    return parser.parse_args(args=args)


def sys_info():
    print("Marvin: %s" % marvin.__version__)
    print("Python: %s" % sys.version.replace('\n', ' - '))
    print("Platform: %s" % sys.platform)
