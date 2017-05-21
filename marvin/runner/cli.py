import argparse

from marvin.runner.runner import Runner


def main(args=None):
    parser = argparse.ArgumentParser(description='Marvin test runner')
    parser.add_argument('tests_path', metavar='DIRECTORY', nargs='?', default='.',
                        help='root directory containing tests')
    parser.add_argument('--config', '-c', dest='config_file',
                        help='path to config file')
    parser.add_argument('--tags', nargs='*', dest='with_tags',
                        help='only run tests containing any of the given tags')
    parser.add_argument('--no-tags', nargs='*', dest='without_tags',
                        help='don\'t run tests containing any of the given tags')

    options = parser.parse_args(args=args)

    Runner(options).start()


if __name__ == '__main__':
    main()
