import sys

from marvin.data.data_providers.null_data_provider import NullDataProvider
from marvin.core.status import Status
from marvin.exceptions import ContextSkippedException
from marvin.report.events import TestStartedEvent, TestEndedEvent, TestSetupStartedEvent, TestSetupEndedEvent, \
    TestIterationStartedEvent, TestIterationEndedEvent, TestTearDownStartedEvent, TestTearDownEndedEvent
from marvin.util import NO_EXCEPTION


class TestRunner(object):
    """
    Internal Marvin Test executor. Implement the logic of a test execution flow, signals, events, etc
    """

    def __init__(self, test_script, data_provider):
        self._test = test_script
        self._data_provider = data_provider or NullDataProvider()
        self._status = None
        self._exceptions = []
        self._skip_iteration = False
        self._skip_teardown = False

    def execute(self):
        self._test_meta_override()
        if not self._should_run_test():
            return
        test_started = TestStartedEvent(self._test, self._data_provider)
        self._test.publisher.notify(test_started)

        self._execute()

        test_ended = TestEndedEvent(self._test, self._data_provider,
                                    test_started.timestamp, self._status, self._exceptions)
        self._test.publisher.notify(test_ended)
        self._test.ctx.sub_context_finished(self._status)

    def _execute(self):
        self._run_phase('setup', self._data_provider.setup_data, TestSetupStartedEvent, TestSetupEndedEvent)

        for iteration in self._data_provider.iterations:
            if self._test.ctx.tags_match(self._iteration_tags(iteration)):
                self._run_phase('run', iteration, TestIterationStartedEvent, TestIterationEndedEvent)

        self._run_phase('tear_down', self._data_provider.tear_down_data,
                        TestTearDownStartedEvent, TestTearDownEndedEvent)

    def _run_phase(self, phase_type, data, started_event_class, ended_event_class):
        if self._should_skip_phase(phase_type):
            return

        status = Status.PASS
        exception = NO_EXCEPTION
        phase_started = started_event_class(self._test, self._data_provider, data)
        self._test.publisher.notify(phase_started)
        try:
            phase_data = data.data if phase_type == 'run' else data
            getattr(self._test, phase_type)(phase_data)
        except ContextSkippedException:
            status = Status.SKIP
            exception = sys.exc_info()
        except:
            status = Status.FAIL
            exception = sys.exc_info()
        finally:
            self._test.publisher.notify(
                ended_event_class(self._test, self._data_provider, data, phase_started.timestamp, status, exception)
            )
            if exception != NO_EXCEPTION:
                self._exceptions.append(exception)
            self._report_phase_status(phase_type, status)

    def _should_run_test(self):
        return any(self._test.ctx.tags_match(self._iteration_tags(iteration))
                   for iteration in self._data_provider.iterations)

    def _iteration_tags(self, iteration):
        return self._test.tags | (iteration.tags or set())

    def _report_phase_status(self, phase_type, status):
        if phase_type == 'setup' and status in [Status.FAIL, Status.SKIP]:
            self._skip_iteration = True
        if phase_type == 'setup' and status == Status.SKIP:
            self._skip_teardown = True
        if phase_type == 'setup' or status == Status.FAIL:
            self._status = status

    def _should_skip_phase(self, phase_type):
        if phase_type == 'tear_down':
            return self._skip_teardown
        if phase_type == 'run':
            return self._skip_iteration
        return False

    def _test_meta_override(self):
        if self._data_provider.name:
            self._test.name = self._data_provider.name
        if self._data_provider.description:
            self._test.description = self._data_provider.description
        tags = self._data_provider.tags
        if isinstance(tags, set):
            self._test.tag(*tags)
