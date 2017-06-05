import time

"""Events that occur in Marvin"""


class EventType(object):
    SUITE_STARTED = 10
    SUITE_ENDED = 20
    TEST_STARTED = 30
    TEST_ENDED = 40
    TEST_SETUP_STARTED = 50
    TEST_SETUP_ENDED = 60
    TEST_ITERATION_STARTED = 70
    TEST_ITERATION_ENDED = 80
    TEST_TEARDOWN_STARTED = 90
    TEST_TEARDOWN_ENDED = 100
    STEP_STARTED = 110
    STEP_ENDED = 120
    STEP_SKIPPED = 130


class Event(object):
    """Abstract root Event class"""
    def __init__(self):
        self._timestamp = int(time.time() * 1000)

    @property
    def timestamp(self):
        """Event timestamp (Unix time with ms granularity)"""
        return self._timestamp


# -- SUITE related events --


class SuiteEvent(Event):
    """Abstract class for all Suite related events"""

    def __init__(self, suite):
        super(SuiteEvent, self).__init__()
        self._suite = suite

    @property
    def suite(self):
        """The Suite instance associated with this event"""
        return self._suite


class SuiteStartedEvent(SuiteEvent):
    """Triggered when a suite is about to start it's execution"""
    event_type = EventType.SUITE_STARTED


class SuiteEndedEvent(SuiteEvent):
    """Triggered when a suite has finished it's execution"""
    event_type = EventType.SUITE_ENDED

    def __init__(self, suite, start_time, status):
        super(SuiteEndedEvent, self).__init__(suite)
        self._start_time = start_time
        self._status = status
        self._duration = self.timestamp - start_time

    @property
    def start_time(self):
        """The timestamp when the suite started"""
        return self._start_time

    @property
    def duration(self):
        """The suite execution time in ms"""
        return self._duration

    @property
    def status(self):
        """The suite's status"""
        return self._status


# -- TEST related events --


class TestEvent(Event):
    """Abstract class for all TestScript related events"""

    def __init__(self, test_script, data_provider):
        super(TestEvent, self).__init__()
        self._test_script = test_script
        self._data_provider = data_provider

    @property
    def test_script(self):
        """The TestScript instance associated with this event"""
        return self._test_script

    @property
    def data_provider(self):
        """The instance of the data provider driving this test execution"""
        return self._data_provider


class TestStartedEvent(TestEvent):
    """Triggered when a test is about to start it's execution"""
    event_type = EventType.TEST_STARTED


class TestEndedEvent(TestEvent):
    """Triggered when a test has finished it's execution"""
    event_type = EventType.TEST_ENDED

    def __init__(self, test_script, data_provider, start_time, status, exceptions):
        super(TestEndedEvent, self).__init__(test_script, data_provider)
        self._start_time = start_time
        self._status = status
        self._exceptions = exceptions
        self._duration = self.timestamp - start_time

    @property
    def start_time(self):
        """The timestamp when the test started"""
        return self._start_time

    @property
    def duration(self):
        """The test execution time in ms"""
        return self._duration

    @property
    def status(self):
        """The test's status"""
        return self._status

    @property
    def exceptions(self):
        """
        The exceptions raised during this test. A list of 3-tuple items (like sys.exc_info)
        composed of (Exception type, Exception instance, Traceback instance)
        """
        return self._exceptions


class TestBlockStartedEvent(TestEvent):
    """Abstract class for test's block started: setup, iteration(s), tear down"""

    def __init__(self, test_script, data_provider, data):
        super(TestBlockStartedEvent, self).__init__(test_script, data_provider)
        self._data = data

    @property
    def data(self):
        """the data for this test block"""
        return self._data


class TestBlockEndedEvent(TestEvent):
    """Abstract class for test's block ended: setup, iteration(s), tear down"""

    def __init__(self, test_script, data_provider, data, start_time, status, exception):
        super(TestBlockEndedEvent, self).__init__(test_script, data_provider)
        self._data = data
        self._start_time = start_time
        self._status = status
        self._exception = exception
        self._duration = self.timestamp - start_time

    @property
    def data(self):
        """the data used by this test block"""
        return self._data

    @property
    def start_time(self):
        """The timestamp when the block started"""
        return self._start_time

    @property
    def duration(self):
        """The block execution time in ms"""
        return self._duration

    @property
    def status(self):
        """The block's status"""
        return self._status

    @property
    def exception(self):
        """
        The exception raised by this block (if any) as a 3-tuple (like sys.exc_info)
        composed of (Exception type, Exception instance, Traceback instance)
        """
        return self._exception


class TestSetupStartedEvent(TestBlockStartedEvent):
    """Triggered when a test's setup phase is about to start"""
    event_type = EventType.TEST_SETUP_STARTED


class TestSetupEndedEvent(TestBlockEndedEvent):
    """Triggered when a test's setup phase has concluded"""
    event_type = EventType.TEST_SETUP_ENDED


class TestIterationStartedEvent(TestBlockStartedEvent):
    """Triggered when a test's iteration is about to start"""
    event_type = EventType.TEST_ITERATION_STARTED


class TestIterationEndedEvent(TestBlockEndedEvent):
    """Triggered when a test's iteration has concluded"""
    event_type = EventType.TEST_ITERATION_ENDED


class TestTearDownStartedEvent(TestBlockStartedEvent):
    """Triggered when a test's tear down phase is about to start"""
    event_type = EventType.TEST_TEARDOWN_STARTED


class TestTearDownEndedEvent(TestBlockEndedEvent):
    """Triggered when a test's tear down phase has concluded"""
    event_type = EventType.TEST_TEARDOWN_ENDED


# -- STEP related events --


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
        composed of (Exception type, Exception instance, Traceback instance)
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
