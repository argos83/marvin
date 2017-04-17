
import inspect
import sys

from marvin.core.status import Status
from marvin.exceptions import ContextSkippedException, ExpectedExceptionNotRaised, StepsFailedInContext
from marvin.report.events import StepStartedEvent, StepEndedEvent, StepSkippedEvent
from marvin.util import compat, NO_EXCEPTION


class StepRunner(object):
    """
    Internal Marvin Step executor. Implement the logic of a step execution flow, signals, events, etc
    """

    def __init__(self, step, args, kwargs):
        self._step = step
        self._args = list(args)  # make args mutable
        self._kwargs = kwargs
        self._execution = None
        self._start_time = None
        self._result = Result(None)
        self._step_exception = NO_EXCEPTION
        self._context_exception = NO_EXCEPTION

    @property
    def result(self):
        return self._result.get()

    def __enter__(self):
        start_event = StepStartedEvent(self._step, self._args, self._kwargs)
        self._start_time = start_event.timestamp
        self._step.publisher.notify(start_event)

        result, self._step_exception = self._do_run()
        self._result.set(result)

        is_exception = self._step_exception != NO_EXCEPTION
        expected = is_exception and self._is_exception_expected(self._step_exception, self._step.expected_exceptions)

        # Decide whether we should yield the result or fail right away
        if is_exception and self._step.safe_exec:
            # TODO: This is more a language constraint than a feature.
            # Alternatively we could make `safely` and `do` to be incompatible.
            # Or find a way to inject an exception to be raised immediately inside the context
            return self._step, self._step_exception

        elif is_exception and not expected:
            self.__exit__(*NO_EXCEPTION)

        return self._step, self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._context_exception = (exc_type, exc_val, exc_tb)
        sub_context_failures = self._any_sub_steps_failed()

        if self._step_exception != NO_EXCEPTION:
            exception = self._step_exception
            status, to_raise = self._when_exception(self._step_exception)
        elif self._context_exception != NO_EXCEPTION:
            exception = self._context_exception
            status, to_raise = self._when_exception(self._context_exception)
        elif sub_context_failures != NO_EXCEPTION:
            exception = sub_context_failures
            status, to_raise = self._when_exception(sub_context_failures)
        else:
            status, to_raise = self._when_no_exception()
            exception = to_raise

        skip_exception = None
        if self._step_exception[0] == ContextSkippedException:
            skip_exception = self._step_exception

        elif self._context_exception[0] == ContextSkippedException:
            skip_exception = self._context_exception

        if skip_exception:
            status = Status.SKIP
            skip_event = StepSkippedEvent(self._step, skip_exception)
            self._step.publisher.notify(skip_event)

        if self._step.shall_pass and status == Status.FAIL:
            status = Status.PASS

        end_event = StepEndedEvent(self._step,
                                   status,
                                   self._result,
                                   self._start_time,
                                   exception)

        self._step.publisher.notify(end_event)

        # Notify the result to the parent context
        self._step.ctx.sub_context_finished(status)

        if to_raise[1] and not self._step.safe_exec:
            raise compat.raise_exc_info(*to_raise)

        return True

    def _do_run(self):
        result = None
        exception = NO_EXCEPTION
        try:
            result = self._step.run(*self._args, **self._kwargs)
        except Exception:
            exception = sys.exc_info()

        return result, exception

    def _any_sub_steps_failed(self):
        failed_subcontexts = self._step.context_summary[Status.FAIL]
        if failed_subcontexts:
            return StepsFailedInContext, StepsFailedInContext(failed_subcontexts), None
        return NO_EXCEPTION

    def _when_no_exception(self):
        if not self._step.expected_exceptions:
            return Status.PASS, NO_EXCEPTION

        to_raise = (ExpectedExceptionNotRaised, ExpectedExceptionNotRaised(self._step.expected_exceptions), None)
        return Status.FAIL, to_raise

    def _when_exception(self, exception):
        was_expected = self._is_exception_expected(exception, self._step.expected_exceptions)
        if self._step.shall_pass or was_expected:
            status = Status.PASS
        else:
            status = Status.FAIL
        if self._step.safe_exec or was_expected:
            to_raise = NO_EXCEPTION
        else:
            to_raise = exception
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
