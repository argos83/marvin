from marvin.core.reportable import Reportable
from marvin.core.context import Context
from marvin.core.step_running_context import StepRunningContext
from marvin.core.test_runner import TestRunner


class TestScript(Context, StepRunningContext, Reportable):
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

    def __init__(self, parent_context):
        Context.__init__(self, parent_context=parent_context)
        StepRunningContext.__init__(self)
        Reportable.__init__(self)
        self._failed_steps = 0

    def setup(self, _data):
        """
        Setup phase of a TestScript, executed only once, before all the iterations
        Can be redefined by subclasses implementing actual tests
        """
        pass

    def run(self, _data):
        """
        Main execution phase, invoked once per each iteration.
        Must be redefined by subclasses
        """
        raise NotImplementedError("Method run must be implemented in test script '%s'" % self.name)

    def tear_down(self, _data):
        """
        Tear down phase of a TestScript, executed only once, after all the iterations (even if there're failures)
        Can be redefined by subclasses implementingactual tests
        """
        pass

    def execute(self, data_provider=None):
        """
        Executes this TestScript with the given data provider
        """
        # TODO: TestScript instances should probably not be allowed to execute more than once
        # Either make them stateless (and allow re-execution) or add controls to fail if executed more than once
        TestRunner(self, data_provider).execute()
