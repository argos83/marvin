from marvin import Step, TestScript
from marvin.core.context import Context
from marvin.core.step_running_context import StepRunningContext
from marvin.core.test_running_context import TestRunningContext


class DummyContext(Context, StepRunningContext, TestRunningContext):

    def observer(self, *event_types):
        return DummyObserver(self.publisher, *event_types)

    def sub_context_finished(self, status):
        super(DummyContext, self).sub_context_finished(status)
        self.last_status = status


class DummyStep(Step):
    """Dummy Step used for testing"""

    def run(self, number_1, number_2, operation=int.__add__):
        return operation(number_1, number_2)


class DummyTest(TestScript):
    """Dummy Test used for testing"""

    def setup(self, data):
        pass

    def run(self, data):
        pass

    def tear_down(self, data):
        pass


class EchoStep(Step):
    """Another Dummy Step"""
    def run(self, *args, **kwargs):
        if 'action' in kwargs:
            return kwargs.pop('action')(self, *args, **kwargs)
        elif 'runtime_error' in kwargs:
            raise RuntimeError(kwargs['runtime_error'])
        return args, kwargs


class DummyObserver(object):

    def __init__(self, publisher, *event_types):
        self.events = []
        publisher.subscribe(self.on_event, *event_types)

    def on_event(self, event):
        self.events.append(event)

    @property
    def last_event(self):
        return self.events[-1]
