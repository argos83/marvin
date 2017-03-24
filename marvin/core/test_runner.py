import sys

from marvin.data.data_providers.null_data_provider import NullDataProvider
from marvin.core.status import Status
from marvin.report.events import TestStartedEvent, TestEndedEvent, TestIterationStartedEvent
from marvin.util import compat


class TestRunner(object):
    """
    Internal Marvin Test executor. Implement the logic of a test execution flow, signals, events, etc
    """

    def __init__(self, test_script, data_provider):
        self._test = test_script
        self._data = data_provider or NullDataProvider()

    def execute(self):
        test_started = TestStartedEvent(self._test, self._data)
        self._test.publisher.notify(test_started)

        # TODO: also generate events for each execution block: setup, iterations, tear_down

        status, exceptions = self._execute()

        test_ended = TestEndedEvent(self, test_started.timestamp, status, exceptions)

        self._test.publisher.notify(test_ended)

        if status == Status.FAIL and exceptions:
            raise compat.raise_exc_info(*exceptions[0])

    def _execute(self):
        exc_info = []
        status = Status.PASS
        try:
            self._test.setup(self._data.setup_data())
            for it_data in self._data.iteration_data():
                self._do_run(it_data, exc_info)

        except:
            exc_info.append(sys.exc_info())
        finally:
            try:
                self._test.tear_down(self._data.tear_down_data())
            except:
                exc_info.append(sys.exc_info())

        if exc_info:
            status = Status.FAIL
        return status, exc_info

    def _do_run(self, data, exc_info):
        iteration_started = TestIterationStartedEvent(self._test, data)
        self._test.publisher.notify(iteration_started)
        try:
            self._test.run(data)
        except:
            exc_info.append(sys.exc_info())
