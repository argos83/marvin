from marvin.core.reportable import Reportable
from marvin.core.step_running_context import StepRunningContext
from marvin.core.step_runner import StepRunner


class Step(StepRunningContext, Reportable):

    def __init__(self, parent_context):
        StepRunningContext.__init__(self, parent_context=parent_context)
        Reportable.__init__(self)
        self._shall_pass = False
        self._safe_exec = False
        self._expected_exceptions = []

    @property
    def do_not_fail(self):
        self._shall_pass = True
        return self

    @property
    def catch_exceptions(self):
        self._safe_exec = True
        return self

    def expect_exception(self, *specs):
        self._expected_exceptions.extend(specs)
        return self

    @property
    def expected_exceptions(self):
        return self._expected_exceptions

    @property
    def shall_pass(self):
        return self._shall_pass

    @property
    def safe_exec(self):
        return self._safe_exec

    def execute(self, *args, **kwargs):
        return StepRunner(self, args, kwargs).execute()

    def run(self, *args, **kargs):
        """Step's logic implementation (to be redefined by sub-classes)"""
        raise NotImplementedError("Method run must be implemented in step '%s'" % self.name)
