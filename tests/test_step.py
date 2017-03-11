import pytest

from marvin import Step
from marvin.exceptions import ContextSkippedException, ExpectedExceptionNotRaised
from marvin.report import EventType
from tests.stubs import DummyStep, EchoStep


def test_step_basic(ctx):
    """Verify a basic step operation"""
    result = ctx.step(DummyStep).execute(2, 4, operation=lambda x, y: x * y)
    assert result == 8


def test_steps_are_reportable(ctx):
    """Steps inherit the capabilities from the Reportable MixIn"""

    # See test_reportable.py to understand the whole set of capabilities

    class SomeStep(Step):
        """Step description"""
        TAGS = ['a', 'few', 'tags']

    step = ctx.step(SomeStep)
    step.tag('and', 'some', 'labels')
    step.untag('a', 'few')

    assert step.name == 'SomeStep'
    assert step.description == 'Step description'
    assert step.tags == {'tags', 'and', 'some', 'labels'}


def test_steps_can_run_other_steps(ctx):
    """Steps are themselves step running contexts"""

    class MacroStep(Step):

        def run(self, add_me):
            intermediate_result = self.step(DummyStep).execute(2, 4, operation=lambda x, y: x * y)
            return intermediate_result + add_me

    result = ctx.step(MacroStep).execute(3)

    assert result == 11


def test_step_events(ctx):
    """Executing a step results """
    observer = ctx.observer(EventType.STEP_STARTED, EventType.STEP_ENDED)

    multiply = lambda x, y: x * y
    ctx.step(DummyStep).execute(2, 4, operation=multiply)

    assert len(observer.events) == 2

    start_event = observer.events[0]
    end_event = observer.events[1]

    assert start_event.timestamp <= end_event.timestamp
    assert start_event.step == end_event.step
    assert start_event.step.name == 'DummyStep'
    assert start_event.args == [2, 4]
    assert start_event.kwargs == {'operation': multiply}

    assert end_event.duration == end_event.timestamp - start_event.timestamp
    assert end_event.result.get() == 8
    assert end_event.status == 'PASS'
    assert end_event.exception == (None, None, None)


def test_plugins_can_change_step_args_and_results(ctx):
    """Plugins can intercept step arguments and results"""

    def arg_changer(start_event):
        start_event.args[0] = 2
        start_event.args[1] = 4
        start_event.kwargs['text'] = 'even'

    def result_changer(end_event):
        end_event.result.set(42)

    ctx.publisher.subscribe(arg_changer, EventType.STEP_STARTED)
    ctx.publisher.subscribe(result_changer, EventType.STEP_ENDED)

    class OnlyEvenNumbersSupported(Step):

        def run(self, number1, number2, text='undefined'):
            assert number1 % 2 == 0
            assert number2 % 2 == 0
            assert text == 'even'

            return number1 + number2

    result = ctx.step(OnlyEvenNumbersSupported).execute(1, 7, text='the answer to life the universe and everything')
    assert result == 42


def test_step_can_be_skipped(ctx):
    observer = ctx.observer(EventType.STEP_SKIPPED, EventType.STEP_ENDED)

    with pytest.raises(ContextSkippedException) as exc_info:
        ctx.step(EchoStep).execute(action=lambda s: s.skip('Kaput'))

    skip_event, end_event = observer.events

    assert skip_event.exception[1] == exc_info.value
    assert skip_event.exception[1].reason == 'Kaput'
    assert skip_event.exception[1].context == skip_event.step
    assert end_event.status == 'SKIP'
    assert end_event.exception == skip_event.exception


def test_step_fails_when_exception_is_raised(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with pytest.raises(ZeroDivisionError) as exc_info:
        ctx.step(EchoStep).execute(action=lambda _: 5 / 0)

    end_event = observer.last_event
    assert end_event.status == 'FAIL'
    assert end_event.exception[1] == exc_info.value
    assert end_event.result.get() is None


def test_step_not_re_raising_exceptions(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    ctx.step(EchoStep).catch_exceptions.execute(action=lambda _: 5 / 0)
    end_event = observer.last_event
    assert end_event.status == 'FAIL'
    assert end_event.exception[0] == ZeroDivisionError
    assert end_event.result.get() is None


def test_step_expecting_exception_class(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    ctx.step(EchoStep).expect_exception(ZeroDivisionError).execute(action=lambda _: 5 / 0)

    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[0] == ZeroDivisionError
    assert end_event.result.get() is None


def test_step_expecting_exception_callable(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    ctx.step(EchoStep).expect_exception(lambda e: str(e).startswith('Oops')).execute(runtime_error='Oops error')
    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[0] == RuntimeError
    assert end_event.result.get() is None


def test_step_expecting_different_exception(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with pytest.raises(RuntimeError) as exc_info:
        ctx.step(EchoStep).expect_exception(AssertionError).execute(runtime_error='different error')
    end_event = observer.last_event

    assert end_event.status == 'FAIL'
    assert end_event.exception[1] == exc_info.value
    assert end_event.result.get() is None


def test_step_expects_exception_but_nothing_raised(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with pytest.raises(ExpectedExceptionNotRaised) as exc_info:
        ctx.step(EchoStep).expect_exception(ZeroDivisionError).execute(action=lambda _: 5 / 1)

    end_event = observer.last_event
    assert end_event.status == 'FAIL'
    assert end_event.exception[1] == exc_info.value
    assert str(end_event.exception[1]) == "No exception was raised, but the expectation was: %s" % ZeroDivisionError
    assert end_event.result.get() == 5


def test_step_matching_one_of_many_exception_expectations(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    ctx.step(EchoStep).expect_exception(ZeroDivisionError,
                                        AssertionError,
                                        "not-a-valid-expectation",
                                        lambda e: str(e) == 'bbb',
                                        lambda e: str(e) == 'aaa').execute(runtime_error='aaa')
    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[0] == RuntimeError
    assert end_event.result.get() is None


def test_step_never_failing(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with pytest.raises(RuntimeError) as exc_info:
        ctx.step(EchoStep).do_not_fail.execute(runtime_error='Error')

    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[1] == exc_info.value
    assert end_event.result.get() is None


def test_step_with_context_manager(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with ctx.step(DummyStep).do(2, 4, operation=lambda x, y: x * y) as (step, result):
        step.tag('dynamic', 'tagging')

    end_event = observer.last_event

    assert result == 8
    assert end_event.result.get() == result
    assert all(tag in end_event.step.tags for tag in ['dynamic', 'tagging'])


def test_step_with_context_returning_tuple(ctx):
    class SubstractBothWaysStep(Step):
        def run(self, operand1, operand2):
            return operand1 - operand2, operand2 - operand1

    results = []
    with ctx.step(SubstractBothWaysStep).do(6, 4) as (step, (result1, result2)):
        results.append(result1)
        results.append(result2)

    assert results == [2, -2]


def test_step_context_not_called_if_error(ctx):
    """Step context not called if errors are raised """
    observer = ctx.observer(EventType.STEP_ENDED)
    invoked = False

    with pytest.raises(ZeroDivisionError) as exc_info:
        with ctx.step(DummyStep).do(5, 0, operation=lambda x, y: x / y):
            invoked = True

    assert not invoked

    end_event = observer.last_event
    assert end_event.status == 'FAIL'
    assert end_event.exception[1] == exc_info.value


def test_step_context_when_catching_exceptions(ctx):
    """
    Step context is called when errors occur if catch_exceptions is enabled
    but receives exc_info instead of result
    """
    invoked = False
    observer = ctx.observer(EventType.STEP_ENDED)

    with ctx.step(DummyStep).catch_exceptions.do(5, 0, operation=lambda x, y: x / y) as (step, exc_info):
        invoked = True

    assert invoked

    end_event = observer.last_event
    assert end_event.status == 'FAIL'
    assert end_event.exception[0] == ZeroDivisionError
    assert end_event.exception == exc_info


def test_step_context_when_do_not_fail(ctx):
    """Step context not called when exceptions are raised even if do_not_fail is enabled"""
    observer = ctx.observer(EventType.STEP_ENDED)
    invoked = False

    with pytest.raises(ZeroDivisionError) as exc_info:
        with ctx.step(DummyStep).do_not_fail.do(5, 0, operation=lambda x, y: x / y):
            invoked = True

    assert not invoked

    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[1] == exc_info.value


def test_step_context_failing(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with pytest.raises(RuntimeError) as exc_info:
        with ctx.step(DummyStep).do(6, 4, operation=lambda x, y: x + y) as (_step, result):
            if result % 2 == 0:
                raise RuntimeError('blah')

    end_event = observer.last_event
    assert end_event.status == 'FAIL'
    assert end_event.exception[1] == exc_info.value


def test_step_context_failing_when_do_not_fail(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with pytest.raises(RuntimeError) as exc_info:
        with ctx.step(DummyStep).do_not_fail.do(6, 4, operation=lambda x, y: x + y) as (_step, result):
            if result % 2 == 0:
                raise RuntimeError('blah')

    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[1] == exc_info.value


def test_step_exception_expectation_applies_for_context(ctx):
    observer = ctx.observer(EventType.STEP_ENDED)

    with ctx.step(EchoStep).expect_exception(ZeroDivisionError).do(action=lambda _: 5 / 1) as (_step, result):
        result / 0

    end_event = observer.last_event
    assert end_event.status == 'PASS'
    assert end_event.exception[0] == ZeroDivisionError


def test_step_context_can_trigger_skip(ctx):
    observer = ctx.observer(EventType.STEP_SKIPPED, EventType.STEP_ENDED)

    with pytest.raises(ContextSkippedException) as exc_info:
        with ctx.step(DummyStep).do(6, 4, operation=lambda x, y: x + y) as (step, _result):
            step.skip('skipping in context')

    skip_event, end_event = observer.events

    assert skip_event.exception[1] == exc_info.value
    assert skip_event.exception[1].reason == 'skipping in context'
    assert skip_event.exception[1].context == skip_event.step
    assert end_event.status == 'SKIP'
    assert end_event.exception == skip_event.exception


def test_step_run_method_not_implemented(ctx):
    class WipStep(Step):
        pass

    observer = ctx.observer(EventType.STEP_ENDED)
    with pytest.raises(NotImplementedError) as exc_info:
        ctx.step(WipStep).execute(1, 2)

    end_event = observer.last_event

    assert end_event.exception[1] == exc_info.value
    assert end_event.status == 'FAIL'
