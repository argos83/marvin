import collections
import inspect
import sys

from marvin.core.status import Status
from marvin.exceptions import ContextSkippedException, ExpectedExceptionNotRaised
from marvin.report.events import StepStartedEvent, StepEndedEvent, StepSkippedEvent
from marvin.util import compat

class StepRunner(object):
    """
    Internal Marvin Step executor. Implement the logic of a step execution flow, signals, events, etc
    """

    Execution = collections.namedtuple('Execution', 'status result exception raise_exception')

    def __init__(self, step, args, kwargs):
        self._step = step
        self._args = list(args)  # make args mutable
        self._kwargs = kwargs
        self._execution = None
        self._start_time = None

    def result(self):
        return self._execution.result.get()

    def __enter__(self):
        start_event = StepStartedEvent(self._step, self._args, self._kwargs)
        self._start_time = start_event.timestamp
        self._step.publisher.notify(start_event)

        self._execution = self._do_run()

        # Decide whether we should yield the result or fail
        if self._execution.raise_exception[1]:
            self.__exit__(None, None, None)

        elif self._step.safe_exec and self._execution.exception[1]:
            # TODO: This is more a language constraint than a feature.
            # Alternatively we could make `catch_exceptions` and `do` to be incompatible.
            # Or find a way to inject an exception to be raised immediately inside the context
            return self._step, self._execution.exception

        return self._step, self._execution.result.get()

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_event = StepEndedEvent(self._step,
                                   self._execution.status,
                                   self._execution.result,
                                   self._start_time,
                                   self._execution.exception)

        self._step.publisher.notify(end_event)

        if self._execution.raise_exception[1]:
            raise compat.raise_exc_info(*self._execution.raise_exception)


    def _do_run(self):
        result = None
        try:
            result = self._step.run(*self._args, **self._kwargs)
            status, raise_exception = self._when_no_exception()
            exception = raise_exception
        except ContextSkippedException:
            status = Status.SKIP
            exception = raise_exception = sys.exc_info()
            self._step.publisher.notify(StepSkippedEvent(self._step, exception))
        except Exception:
            exception = sys.exc_info()
            status, raise_exception = self._when_exception(exception)
        return self.Execution(status=status,
                              result=Result(result),
                              exception=exception,
                              raise_exception=raise_exception)

    def _when_no_exception(self):
        if not self._step.expected_exceptions:
            return Status.PASS, (None, None, None)

        to_raise = (ExpectedExceptionNotRaised, ExpectedExceptionNotRaised(self._step.expected_exceptions), None)
        return Status.FAIL, to_raise

    def _when_exception(self, exception):
        was_expected = self._is_exception_expected(exception, self._step.expected_exceptions)
        status = Status.PASS if self._step.shall_pass or was_expected else Status.FAIL
        to_raise = (None, None, None) if self._step.safe_exec or was_expected else exception
        return status, to_raise

    def _is_exception_expected(self, exception, expectation):
        exc_type, exc_val, exc_tb = exception
        if isinstance(expectation, list):
            return any(self._is_exception_expected(exception, expect) for expect in expectation)
        if inspect.isclass(expectation):
            return issubclass(expectation, exc_type)
        if callable(expectation):
            return expectation(exc_val)
        return False


class Result(object):
    """
    Wraps a step result so plugins can change its value even if type is immutable
    """
    def __init__(self, result):
        self._result = result

    def get(self):
        """Get the step result object"""
        return self._result

    def set(self, value):
        """Change the step result object"""
        self._result = value
