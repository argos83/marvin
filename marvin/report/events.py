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
    """Abstract root Event class"""
    def __init__(self):
        self._timestamp = int(time.time() * 1000)

    @property
    def timestamp(self):
        """Event timestamp (Unix time with ms granularity)"""
        return self._timestamp


class StepEvent(Event):
    """Abstract class for all Step related events"""
    def __init__(self, step):
        super(StepEvent, self).__init__()
        self._step = step

    @property
    def step(self):
        """The step instance associated with this event"""
        return self._step


class StepStartedEvent(StepEvent):
    """Triggered when a Step is about to be executed"""
    event_type = EventType.STEP_STARTED

    def __init__(self, step, args, kwargs):
        super(StepStartedEvent, self).__init__(step)
        self._args = args
        self._kwargs = kwargs

    @property
    def args(self):
        """The arguments being passed to the step's run method"""
        return self._args

    @property
    def kwargs(self):
        """The keyword arguments being passed to the step's run method"""
        return self._kwargs


class StepEndedEvent(StepEvent):
    """Triggered when a Step has finished it's execution"""
    event_type = EventType.STEP_ENDED

    def __init__(self, step, status, result, start_time, exception=(None, None, None)):
        super(StepEndedEvent, self).__init__(step)
        self._status = status
        self._result = result
        self._start_time = start_time
        self._duration = self.timestamp - start_time
        self._exception = exception

    @property
    def status(self):
        """The step's status"""
        return self._status

    @property
    def result(self):
        """The step's returned result (wrapped in a Result instance)"""
        return self._result

    @property
    def start_time(self):
        """The timestamp when the step started"""
        return self._start_time

    @property
    def duration(self):
        """The step execution time in ms"""
        return self._duration

    @property
    def exception(self):
        """
        The exception raised by this step (if any) as a 3-tuple (like sys.exc_info)
        composed of (Exception type, Exception isntance, Traceback instance)
        """
        return self._exception


class StepSkippedEvent(StepEvent):
    """Triggered when a step is being skipped"""
    event_type = EventType.STEP_SKIPPED

    def __init__(self, step, exception):
        super(StepSkippedEvent, self).__init__(step)
        self._exception = exception

    @property
    def exception(self):
        """
        The corresponding ContextSkippedException containing the reason and stacktrace
        as a 3-tuple (like sys.exc_info) composed of (Exception type, Exception isntance, Traceback instance)
        """
        return self._exception
