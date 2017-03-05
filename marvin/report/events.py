import time

"""Events that occur in Marvin"""


class EventType(object):
    SUITE_STARTED = 10
    SUITE_ENDED = 20
    TEST_STARTED = 30
    TEST_ENDED = 40
    STEP_STARTED = 50
    STEP_ENDED = 60
    STEP_SKIPPED = 70
    ALL = [
        SUITE_STARTED,
        SUITE_ENDED,
        TEST_STARTED,
        TEST_ENDED,
        STEP_STARTED,
        STEP_ENDED,
        STEP_SKIPPED
    ]

class Event(object):

    def __init__(self):
        self._timestamp = int(time.time() * 1000)

    @property
    def timestamp(self):
        return self._timestamp


class StepEvent(Event):

    def __init__(self, step):
        super(StepEvent, self).__init__()
        self._step = step

    @property
    def step(self):
        return self._step


class StepStartedEvent(StepEvent):
    event_type = EventType.STEP_STARTED

    def __init__(self, step, args, kwargs):
        super(StepStartedEvent, self).__init__(step)
        self._args = args
        self._kwargs = kwargs

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs


class StepEndedEvent(StepEvent):
    event_type = EventType.STEP_ENDED

    def __init__(self, step, status, result, start_time, exception=None):
        super(StepEndedEvent, self).__init__(step)
        self._status = status
        self._result = result
        self._start_time = start_time
        self._duration = self.timestamp - start_time
        self._exception = exception

    @property
    def status(self):
        return self._status

    @property
    def result(self):
        return self._result

    @property
    def start_time(self):
        return self._start_time

    @property
    def duration(self):
        return self._duration

    @property
    def exception(self):
        return self._exception