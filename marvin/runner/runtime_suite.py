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
        self._data_extensions = DataProviderRegistry.supported_file_extensions()
        self._load_config(config_file=config_file,
                          tests_path=tests_path,
                          with_tags=with_tags,
                          without_tags=without_tags)
        self._load_hook_module()
        self._root_dir = self.cfg.marvin.get('tests_path', '.')
        self._filter = Filter.from_config(self.cfg.marvin.get('filter', {}))

    def tests(self):
        class_loader = ClassLoader(TestScript)

        ts_filter = TestScriptFilter(self._filter)
        ts_finder = FileFinder(ts_filter, self._root_dir)

        for ts_file in ts_finder.find_all():
            ts_dir, filename = os.path.split(ts_file)
            ts_id, _ = os.path.splitext(filename)

            mod = compat.import_module(ts_id, ts_file)

            ts_class = class_loader.find(mod)
            if not ts_class:
                continue

            if not self._filter.by_tags(ts_class.class_tags()):
                continue

            for data_provider in self._find_data_for_test_script(ts_id, ts_dir):
                yield ts_class, data_provider

    def _find_data_for_test_script(self, ts_id, directory):
        data_file_filter = DataFileFilter(self._filter, ts_id, self._data_extensions)
        file_finder = FileFinder(data_file_filter, directory)

        data_found = False
        for data_file in file_finder.find_all():
            provider = DataProviderRegistry.data_provider_for(data_file)

            if not provider:
                continue

            data_found = True
            yield provider

        if not data_found and self._filter.by_data_id(None):
            provider = DataProviderRegistry.data_provider_for(None)
            if provider:
                yield provider

    def _load_config(self, **options):
        self.cfg.set('marvin', default_config())

        cfg_file = (options.get('config_file') or os.environ.get('MARVIN_CONFIG') or
                    next((path for path in ['marvin.yaml', 'marvin.yml', 'marvin.json'] if os.path.isfile(path)), None))
        if cfg_file:
            self.cfg.load_into('marvin', cfg_file)

        self.cfg.set('marvin', self._override_config(options))
        self._load_env_settings()

    def _override_config(self, options):
        settings = {}
        if options.get('tests_path'):
            settings['tests_path'] = options['tests_path']
        if options.get('with_tags'):
            settings.setdefault('filter', {})['with_tags'] = options['with_tags']
        if options.get('without_tags'):
            settings.setdefault('filter', {})['without_tags'] = options['without_tags']
        return settings

    def _load_env_settings(self):
        env = os.environ.get('MARVIN_ENV', self.cfg.marvin.get('env'))
        env_files_glob = self.cfg.marvin.get('environments', {}).get(env, [])
        for glob_matcher in env_files_glob:
            self.cfg.load(*glob.glob(glob_matcher))

    def _load_hook_module(self):
        file_name = self.cfg.marvin.get('hook_module')
        if not (file_name and os.path.isfile(file_name)):
            return
        mod = compat.import_module('marvin_hook', file_name)
        if hasattr(mod, 'main') and callable(mod.main):
            mod.main(self.publisher, self.cfg)


class Filter(object):
    def __init__(self, tc_id_matcher=None, tags_matcher=None, data_id_matcher=None):
        self._tc_id_matcher = tc_id_matcher or (lambda tc_id: True)
        self._tags_matcher = tags_matcher or (lambda tags: True)
        self._data_id_matcher = data_id_matcher or (lambda data_id: True)

    @classmethod
    def from_config(cls, filter_config):
        w_tags = set(filter_config.get('with_tags', []))
        wo_tags = set(filter_config.get('without_tags', []))

        return cls(tags_matcher=lambda tags: (not w_tags or (tags & w_tags)) and not (tags & wo_tags))

    def by_tc_id(self, tc_id):
        return self._tc_id_matcher(tc_id)

    def by_data_id(self, data_id):
        return self._data_id_matcher(data_id)

    def by_tags(self, tags):
        return self._tags_matcher(tags)


class TestScriptFilter(object):
    def __init__(self, filter):
        self._filter = filter

    def __call__(self, filename):
        file_id, ext = os.path.splitext(filename)
        return ext.lower() == '.py' and self._filter.by_tc_id(file_id)


class DataFileFilter(object):
    def __init__(self, filter, tc_file_id, supported_extensions):
        self._filter = filter
        self._tc_file_id = tc_file_id
        self._extensions = supported_extensions

    def __call__(self, filename):
        parts = filename.split('.')
        return (len(parts) > 1
                and parts[0] == self._tc_file_id
                and parts[-1] in self._extensions
                and self._filter.by_data_id(".".join(parts[1:-1])))
