from marvin.core.reportable import Reportable
from marvin.core.context import Context
from marvin.core.step_running_context import StepRunningContext
from marvin.core.step_runner import StepRunner


class Step(Context, StepRunningContext, Reportable):

    def __init__(self, parent_context):
        Context.__init__(self, parent_context=parent_context)
        StepRunningContext.__init__(self)
        Reportable.__init__(self)
        self._shall_pass = False
        self._safe_exec = False
        self._expected_exceptions = []

    @property
    def do_not_fail(self):
        """
        Flag this step as 'optional' and set the status to PASS even if it fails
        Notice that the step may still raise exceptions that you might want to catch
        or silently ignore them via `safely`.
        """
        self._shall_pass = True
        return self

    @property
    def safely(self):
        """
        Don't propagate exceptions raised by this step
        (the status will still be set to FAIL unless `do_not_fail` is used.
        """
        self._safe_exec = True
        return self

    def expect_exception(self, *specs):
        """
        Expect this step to raise any of the given exception expectations.
        Each expectation can be either:
            * a Exception class. E.g. RuntimeError
            * a callable receiving the exception instance as argument and returning
            a Truthy value if the exception was expected. E.g. lambda e: isintance(e, HTTPError) and e.code == 404

        If exception expectations have been defined and the step raises no exception,
        then a ExpectedExceptionNotRaised is raised and the step status set to FAIL
        """
        self._expected_exceptions.extend(specs)
        return self

    def execute(self, *args, **kwargs):
        """
        Executes the step
        """
        runner = self.do(*args, **kwargs)
        with runner:
            pass

        return runner.result

    def do(self, *args, **kwargs):
        return StepRunner(self, args, kwargs)

    @property
    def expected_exceptions(self):
        """
        INTERNAL USE
        :return: a list of all defined exception expectations
        """
        return self._expected_exceptions

    @property
    def shall_pass(self):
        """
        INTERNAL USE
        :return: True if `do_no_fail` was set, False otherwise
        """
        return self._shall_pass

    @property
    def safe_exec(self):
        """
        INTERNAL USE
        :return: True if `safely` was set, False otherwise
        """
        return self._safe_exec

    def run(self, *args, **kargs):
        """Step's logic implementation (to be redefined by sub-classes)"""
        raise NotImplementedError("Method run must be implemented in step '%s'" % self.name)
