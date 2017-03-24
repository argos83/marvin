from marvin.core.context import Context
from marvin.core.status import Status


class StepRunningContext(Context):
    """
    An abstraction of a Context that is allowed to run steps.
    E.g. TestScripts, and Steps contexts can run steps
    """

    def __init__(self, *args, **kwargs):
        super(StepRunningContext, self).__init__(*args, **kwargs)
        self._sub_context_results = {
            Status.PASS: 0,
            Status.FAIL: 0,
            Status.SKIP: 0
        }

    def step(self, step_class):
        """Instantiates a new step with this as it's parent context"""
        return step_class(self)

    # Override
    def sub_context_finished(self, status):
        """Keep count of steps failed within this context"""
        self._sub_context_results[status] += 1
