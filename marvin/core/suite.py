import time

from marvin.core.context import Context
from marvin.core.reportable import Reportable
from marvin.report import Publisher, Events


class Suite(Context, Reportable):

    def __init__(self):
        Context.__init__(self, parent_context=None)
        Reportable.__init__(self)

    def execute(self):
        start = int(time.time() * 1000)
        data = {
        "suite": self,
        "timestamp": start
        }

        Publisher.notify(Events.SUITE_STARTED, data)

        status = self._execute()

        # TODO: add more info (number of tests, passed/failed, etc)
        data = {"suite": self,
                "status": status,
                "start_time": start,
                "timestamp": int(time.time() * 1000)}

        Publisher.notify(Events.SUITE_ENDED, data)

    def tests(self):
        """To be redefined by specific Suite implementations. The method must return
        an iterable object (e.g. a list or a generator) of test object."""

        raise NotImplementedError("Method run must be redefined")

    def _execute(self):
        for test in self.tests():
            test.execute()
        return "PASSED"