import os
import glob

from marvin import Suite, TestScript
from marvin.util.files import ClassLoader, FileFinder
from marvin.util import compat
from marvin.data import DataProviderRegistry


def default_config():
    return {
        'tests_path': '.',
        'filter': {
            'with_tags': [],
            'without_tags': []
        },
        'hook_module': 'marvin_conf.py',
        'env': None,
        'environments': {}
    }


class RuntimeSuite(Suite):
    def __init__(self, config_file=None, tests_path=None, with_tags=None, without_tags=None):
        super(RuntimeSuite, self).__init__()
        self._supported_data_file_extensions = DataProviderRegistry.supported_file_extensions()
        self._load_marvin_config(config_file=config_file,
                                 tests_path=tests_path,
                                 with_tags=with_tags,
                                 without_tags=without_tags)
        self._load_test_environment_config()
        self._load_hook_module()
        self._root_dir = self.cfg.marvin.get('tests_path', '.')

    def tests(self):
        test_script_class_loader = ClassLoader(TestScript)

        python_file_finder = FileFinder(self._root_dir,
                                        filename_matcher=lambda name: name.lower().endswith('.py'))

        tags_matcher = self._tags_matcher()

        for python_file in python_file_finder.find_all():
            directory, filename = os.path.split(python_file)
            filename_base, _ = os.path.splitext(filename)

            mod = compat.import_module(python_file, module_name=filename_base)

            test_script_class = test_script_class_loader.find(mod)
            if not test_script_class:
                continue

            if not tags_matcher(test_script_class.class_tags()):
                continue

            test_script_id = filename_base
            for data_provider in self._find_data_for_test_script(test_script_id, directory):
                yield test_script_class, data_provider

    def _find_data_for_test_script(self, test_script_id, test_script_directory):
        data_file_matcher = DataFileMatcher(test_script_id, self._supported_data_file_extensions)
        data_file_finder = FileFinder(test_script_directory, filename_matcher=data_file_matcher)

        data_found = False
        for data_file in data_file_finder.find_all():
            provider = DataProviderRegistry.data_provider_for(data_file)

            if not provider:
                continue

            data_found = True
            yield provider

        if not data_found:
            provider = DataProviderRegistry.data_provider_for(None)
            if provider:
                yield provider

    def _load_marvin_config(self, **options):
        self.cfg.set('marvin', default_config())

        cfg_file = (options.get('config_file') or os.environ.get('MARVIN_CONFIG') or
                    next((path for path in ['marvin.yaml', 'marvin.yml', 'marvin.json'] if os.path.isfile(path)), None))
        if cfg_file:
            self.cfg.load_into('marvin', cfg_file)

        cli_overrides = {}
        if options.get('tests_path'):
            cli_overrides['tests_path'] = options['tests_path']
        if options.get('with_tags'):
            cli_overrides.setdefault('filter', {})['with_tags'] = options['with_tags']
        if options.get('without_tags'):
            cli_overrides.setdefault('filter', {})['without_tags'] = options['without_tags']

        self.cfg.set('marvin', cli_overrides)

    def _load_test_environment_config(self):
        env = os.environ.get('MARVIN_ENV', self.cfg.marvin.get('env'))
        env_files_globs = self.cfg.marvin.get('environments', {}).get(env, [])
        for glob_matcher in env_files_globs:
            self.cfg.load(*glob.glob(glob_matcher))

    def _load_hook_module(self):
        file_name = self.cfg.marvin.get('hook_module')
        if not (file_name and os.path.isfile(file_name)):
            return
        mod = compat.import_module(file_name, module_name='marvin_hook')
        if hasattr(mod, 'main') and callable(mod.main):
            mod.main(self.publisher, self.cfg)

    def _tags_matcher(self):
        filter_config = self.cfg.marvin.get('filter', {})

        w_tags = set(filter_config.get('with_tags', []))
        wo_tags = set(filter_config.get('without_tags', []))

        return lambda tags: (not w_tags or (tags & w_tags)) and not (tags & wo_tags)


class DataFileMatcher(object):
    """
    Callable that returns True if the given filename starts with
    the the test script id, and has a supported data extension
    """
    def __init__(self, test_script_id, supported_data_file_extensions):
        self._test_script_id = test_script_id
        self._extensions = supported_data_file_extensions

    def __call__(self, filename):
        parts = filename.split('.')
        return (len(parts) > 1
                and parts[0] == self._test_script_id
                and parts[-1] in self._extensions)
