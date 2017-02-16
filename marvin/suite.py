import time

from marvin.report.publisher import Publisher, Events

class Suite(object):

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