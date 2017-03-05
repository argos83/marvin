
from marvin.report.events import StepStartedEvent, StepEndedEvent


STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"


class StepRunner(object):

    def __init__(self, step, args, kwargs):
        self._step = step
        self._args = args
        self._kwargs = kwargs

    def execute(self):
        start_event = StepStartedEvent(self._step, self._args, self._kwargs)
        self._step.publisher.notify(start_event)

        status, result, exception, raise_exception = self._do_run()

        end_event = StepEndedEvent(self._step, status, result, start_event.timestamp, exception)
        self._step.publisher.notify(end_event)
        if raise_exception:
            raise raise_exception

        return result

    def _do_run(self):
        try:
            result = self._step.run(*self._args, **self._kwargs)
            exception = None
            status, raise_exception = self._when_no_exception()
        except Exception as e:
            exception = result = e
            status, raise_exception = self._when_exception(e)
        return status, result, exception, raise_exception

    def _when_no_exception(self):
        ee = self._step.expected_exceptions
        if not ee:
            return STATUS_PASS, None

        expectation = ee[0] if len(ee) == 1 else ee
        to_raise = RuntimeError("No exception was raised, but the expectation was: %s" % expectation)
        return STATUS_FAIL, to_raise

    def _when_exception(self, exception):
        was_expected = self._is_exception_expected(exception, self._step.expected_exceptions)
        status = STATUS_PASS if self._step.shall_pass or was_expected else STATUS_FAIL
        to_raise = None if self._step.safe_exec or was_expected else exception
        return status, to_raise

    def _is_exception_expected(self, exception, expectation):
        if isinstance(expectation, list):
            return any(self._is_exception_expected(exception, expect) for expect in expectation)
        if issubclass(expectation, BaseException):
            return isinstance(exception, expectation)
        if callable(expectation):
            return expectation(exception)
        return False
