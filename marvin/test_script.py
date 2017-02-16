import time
import sys

from marvin.report.publisher import Publisher, Events

class TestScript(object):
    """
    Base TestScript class to be extended by specific tests.
    Subclasses must re-implement the 'run' method, and can re-implement (if needed)
    the 'setup' and 'tear_down' methods.

    The execution of a test consist of:
        1. Execution of the 'setup' block
        2. One or more executions of the 'run' block
        3. Execution of the 'tear_down' block

    Each of these methods will be called passing as argument an object representing data
    for the block (usually this will be a python dictionary). The data is obtained from a
    DataProvider object, which should be capable of providing data for:
        * The 'setup' block.
        * One or more iteration data for the 'run' block (so it's up to the data provider to
            define how many iterations there will be)
        * The 'tear_down' block.
    """

    def __init__(self, data_provider):
        self._data_provider = data_provider

    def setup(self, _data):
        pass

    def run(self, _data):
        raise NotImplementedError("Method run must be redefined")

    def tear_down(self, _data):
        pass

    @property
    def name(self):
        return getattr(self.__class__, "NAME", self.__class__.__name__)

    @property
    def description(self):
        return getattr(self.__class__, "DESCRIPTION", "")

    @property
    def tags(self):
        return getattr(self.__class__, "TAGS", [])

    def execute(self):
        start = int(time.time() * 1000)
        data = {
        "test_script": self,
        "timestamp": start
        }

        Publisher.notify(Events.TEST_STARTED, data)

        # TODO: also generate events for each execution block: setup, iterations, tear_down

        status, exceptions = self._execute()

        data = {"test_script": self,
                "status": status,
                "start_time": start,
                "exception": exceptions,
                "timestamp": int(time.time() * 1000)}

        Publisher.notify(Events.TEST_ENDED, data)

        if status == "FAILED" and exceptions:
            raise exceptions[0][0], exceptions[0][1], exceptions[0][2]

    # private methods

    def _execute(self):
        exc_info = []
        status = "PASSED"
        try:
            self.setup(self._data_provider.setup_data())
            for it_data in self._data_provider.iteration_data():
                self._do_run(it_data, exc_info)

        except:
            exc_info.append(sys.exc_info())
        finally:
            try:
                self.tear_down(self._data_provider.tear_down_data())
            except:
                exc_info.append(sys.exc_info())

        if exc_info:
            status = "FAILED"
        return status, exc_info

    def _do_run(self, data, exc_info):
        try:
            self.run(data)
        except:
            exc_info.append(sys.exc_info())
