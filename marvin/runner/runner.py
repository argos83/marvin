import os
import sys

from marvin import Suite, TestScript
from marvin.core.status import Status
from marvin.util.files import ClassLoader, FileFinder
from marvin.util import compat
from marvin.data import DataProviderRegistry


class Runner(object):
    def __init__(self, options):
        self._options = options
        self._suite = None
        self._setup_env()
        self._build_suite()
        self._load_config()

    def run(self):
        status = self._suite.execute()
        return 0 if status in [Status.PASS, Status.SKIP] else 1

    def _setup_env(self):
        sys.path.insert(1, '.')

    def _load_config(self):
        cfg_path = self._options.config or os.environ.get('MARVIN_CONFIG') or self._find_config()
        if cfg_path:
            self._suite.cfg.load_into('marvin', cfg_path)
        else:
            self._suite.cfg.set('marvin', {})

    def _find_config(self):
        return next((path for path in ['marvin.yaml', 'marvin.yml', 'marvin.json'] if os.path.isfile(path)), None)

    def _build_suite(self):
        test_filter = Filter.from_options(self._options)
        self._suite = RuntimeSuite(self._options.tests_path, test_filter)
        from marvin.report.observers.event_logger import EventLogger
        EventLogger(self._suite.publisher)


class Filter(object):
    def __init__(self, tc_id_matcher=None, tags_matcher=None, data_id_matcher=None):
        self._tc_id_matcher = tc_id_matcher or (lambda tc_id: True)
        self._tags_matcher = tags_matcher or (lambda tags: True)
        self._data_id_matcher = data_id_matcher or (lambda data_id: True)

    @classmethod
    def from_options(cls, options):
        w_tags = set(options.with_tags or [])
        wo_tags = set(options.without_tags or [])

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


class RuntimeSuite(Suite):
    def __init__(self, tests_dir, filter):
        super(RuntimeSuite, self).__init__()
        self._root_dir = tests_dir
        self._filter = filter
        self._data_extensions = DataProviderRegistry.supported_file_extensions()

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
