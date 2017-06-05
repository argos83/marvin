
from marvin.core.context import Context
from marvin.core.reportable import Reportable
from marvin.core.status import Status
from marvin.core.test_running_context import TestRunningContext
from marvin.report.events import SuiteStartedEvent, SuiteEndedEvent


class Suite(Context, TestRunningContext, Reportable):
    """
    A context representing a collection of tests
    """

    def __init__(self):
        Context.__init__(self, parent_context=None)
        TestRunningContext.__init__(self)
        Reportable.__init__(self)

    def execute(self):
        """
        Executes the tests in this suite
        """
        start_event = SuiteStartedEvent(self)
        self.publisher.notify(start_event)

        status = self._execute()

        self.publisher.notify(SuiteEndedEvent(self, start_event.timestamp, status))
        return status

    def tests(self):
        """To be redefined by specific Suite implementations. The method must return
        an iterable object (e.g. a list or a generator) of tuples (."""

        raise NotImplementedError("Method run must be redefined")

    def _execute(self):
        # TODO: subclasses should be able to define how tests are executed (e.g. allowing parallel execution)
        for test_class, data_provider in self.tests():
            self.test(test_class).execute(data_provider=data_provider)

        if self.context_summary[Status.FAIL]:
            return Status.FAIL
        elif self.context_summary[Status.PASS]:
            return Status.PASS
        return Status.SKIP
