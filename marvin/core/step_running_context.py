from marvin.core.context import Context


class StepRunningContext(object):
    """
    A Mix-In for contexts that are allowed to run steps.
    E.g. TestScripts, and Steps contexts can run steps
    """

    def __init__(self):
        assert isinstance(self, Context)

    def step(self, step_class):
        """Instantiates a new step with this as it's parent context"""
        # TODO: assert step_class is subclass of Step
        return step_class(self)
