import sys

from marvin.core.status import Status
from marvin.runner.runtime_suite import RuntimeSuite
from marvin.report.observers.event_logger import EventLogger


class Runner(object):
    def __init__(self, options):
        self._setup_env()
        self._suite = RuntimeSuite(config_file=options.config, tests_path=options.tests_path,
                                   with_tags=options.with_tags, without_tags=options.without_tags)
        self._load_observers()

    def run(self):
        status = self._suite.execute()
        return 0 if status in [Status.PASS, Status.SKIP] else 1

    def _setup_env(self):
        sys.path.insert(1, '.')

    def _load_observers(self):
        EventLogger(self._suite.publisher)
