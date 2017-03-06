from marvin import Step
from marvin.report import EventType
from stubs import DummyStep


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
    assert step.tags == set(['tags', 'and', 'some', 'labels'])


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
    assert end_event.exception is None


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
