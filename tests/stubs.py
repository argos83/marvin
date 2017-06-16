from marvin import Step, Suite, TestScript
from marvin.data.data_provider import DataProvider
from marvin.core.context import Context
from marvin.core.step_running_context import StepRunningContext
from marvin.core.test_running_context import TestRunningContext


class DummyContext(Context, StepRunningContext, TestRunningContext):

    def observer(self, *event_types):
        return DummyObserver(self.publisher, *event_types)

    def sub_context_finished(self, status):
        super(DummyContext, self).sub_context_finished(status)
        self.last_reported_status = status


class DummyObserver(object):

    def __init__(self, publisher, *event_types):
        self.events = []
        self.hooks = {}
        publisher.subscribe(self.on_event, *event_types)

    def hook(self, fn, *event_types):
        for event_type in event_types:
            self.hooks[event_type] = fn

    def on_event(self, event):
        self.events.append(event)
        if event.event_type in self.hooks:
            self.hooks[event.event_type](event)

    @property
    def last_event(self):
        return self.events[-1]


class DummySuite(Suite):

    def __init__(self):
        super(DummySuite, self).__init__()
        self._tests = []

    def add_test(self, test, data=None):
        self._tests.append((test, data))

    def tests(self):
        for t in self._tests:
            yield t

    def observer(self, *event_types):
        return DummyObserver(self.publisher, *event_types)


class DummyData(DataProvider):
    """In-memory data provider that can be built dynamically"""
    def __init__(self):
        super(DummyData, self).__init__(None)
        self._data = {
            'meta': {},
            'setup': {},
            'iterations': [],
            'tear_down': {}
        }

    # Override
    def meta(self):
        return self._data['meta']

    # Override
    def setup_data(self):
        return self._data['setup']

    # Override
    def iteration_data(self):
        return self._data['iterations'] or [{}]

    # Override
    def tear_down_data(self):
        return self._data['tear_down']

    def with_meta(self, **kwargs):
        self._data['meta'] = kwargs
        return self

    def with_setup(self, **kwargs):
        self._data['setup'] = kwargs
        return self

    def with_iteration(self, **kwargs):
        self._data['iterations'].append(kwargs)
        return self

    def with_tear_down(self, **kwargs):
        self._data['tear_down'] = kwargs
        return self


class DummyTest(TestScript):
    """Dummy Test used for testing"""

    def setup(self, data):
        self._do_something(data)

    def run(self, data):
        self._do_something(data)

    def tear_down(self, data):
        self._do_something(data)

    def _do_something(self, data):
        if 'fail' in data:
            raise Exception(data['fail'])
        if 'skip' in data:
            self.skip(data['skip'])


class SampleStep(Step):
    """Dummy Step used for testing"""

    def run(self, number_1, number_2, operation=int.__add__):
        return operation(number_1, number_2)


class DummyStep(Step):
    """Another Dummy Step"""
    def run(self, *args, **kwargs):
        if 'action' in kwargs:
            return kwargs.pop('action')(self, *args, **kwargs)
        elif 'skip' in kwargs:
            self.skip(kwargs['skip'])
        elif 'runtime_error' in kwargs:
            raise RuntimeError(kwargs['runtime_error'])
        return args, kwargs
