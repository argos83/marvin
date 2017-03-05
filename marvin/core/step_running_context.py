from marvin.core.context import Context


class StepRunningContext(Context):

    def step(self, step_class):
        # TODO: check step_class is a step subclass
        return step_class(self)
