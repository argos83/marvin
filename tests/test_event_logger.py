import contextlib
import time

from freezegun import freeze_time

from marvin.core.status import Status
from marvin.exceptions import ContextSkippedException
from marvin.report.observers.event_logger import EventLogger
from marvin.report import events as E
from marvin.util import compat
from tests.stubs import DummyStep, DummyData, DummyTest, IterationDataBuilder, TracebackBuilder


@contextlib.contextmanager
def event_logger_context(ctx):
    out = compat.string_io()
    publisher = ctx.publisher
    EventLogger(publisher, dest=out)
    with freeze_time():
        yield publisher, out


def milliseconds(ms):
    return int(time.time() * 1000) + ms


def test_step_events(ctx):
    a_traceback = TracebackBuilder().with_frame('file.py', 'raise error', 4).with_frame('other.py', '5/0', 8).build()

    step = ctx.step(DummyStep)
    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.StepStartedEvent(step, 1, {}))
    assert out.getvalue().strip() == 'DummyStep: Another Dummy Step'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.StepEndedEvent(step, Status.PASS, 'result', milliseconds(0)))
    assert out.getvalue().strip() == '[PASS] DummyStep (0 ms)'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.StepEndedEvent(step, Status.PASS, 'result', milliseconds(-1566)))
    assert out.getvalue().strip() == '[PASS] DummyStep (1.57 s)'

    some_exception = (ValueError, ValueError('oops'), a_traceback)
    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.StepEndedEvent(step, Status.FAIL, 'result', milliseconds(-999), some_exception))
    assert out.getvalue().strip().split('\n') == [
        '[FAIL] DummyStep (999 ms)',
        "ValueError('oops',)",
        '  File "file.py", line 4, in raise error',
        '  File "other.py", line 8, in 5/0'
    ]

    skip_exception = (ContextSkippedException, ContextSkippedException(ctx, 'not supported'), a_traceback)
    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.StepEndedEvent(step, Status.SKIP, 'result', milliseconds(-1000), skip_exception))
    assert out.getvalue().strip().split('\n') == [
        '[SKIP] DummyStep (1.00 s)',
        '  Skip reason: not supported'
    ]


def test_iteration_events(ctx):
    test = ctx.test(DummyTest)
    data = DummyData()
    anon_iteration = IterationDataBuilder().build()
    name_iteration = IterationDataBuilder().with_name('My Iteration').build()
    desc_iteration = IterationDataBuilder().with_description('blah blah').build()
    full_iteration = IterationDataBuilder().with_name('My Iteration').with_description('blah blah').build()

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationStartedEvent(test, data, anon_iteration))
    assert out.getvalue().strip() == '[ITERATION]'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationStartedEvent(test, data, name_iteration))
    assert out.getvalue().strip() == '[ITERATION] My Iteration'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationStartedEvent(test, data, desc_iteration))
    assert out.getvalue().strip() == '[ITERATION]: blah blah'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationStartedEvent(test, data, full_iteration))
    assert out.getvalue().strip() == '[ITERATION] My Iteration: blah blah'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationEndedEvent(test, data, anon_iteration, milliseconds(0), Status.PASS, None))
    assert out.getvalue().strip() == '[ITERATION - PASS] (0 ms)'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationEndedEvent(test, data, name_iteration, milliseconds(-999), Status.FAIL, None))
    assert out.getvalue().strip() == '[ITERATION - FAIL] My Iteration (999 ms)'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestIterationEndedEvent(test, data, full_iteration, milliseconds(-1567), Status.SKIP, None))
    assert out.getvalue().strip() == '[ITERATION - SKIP] My Iteration (1.57 s)'


def test_setup_teardown_events(ctx):
    test = ctx.test(DummyTest)
    data = DummyData()

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestSetupStartedEvent(test, data, None))
    assert out.getvalue().strip() == '[SETUP]'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestTearDownStartedEvent(test, data, None))
    assert out.getvalue().strip() == '[TEARDOWN]'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestSetupEndedEvent(test, data, None, milliseconds(-500), Status.PASS, None))
    assert out.getvalue().strip() == '[SETUP - PASS] (500 ms)'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestTearDownEndedEvent(test, data, None, milliseconds(-1500), Status.FAIL, None))
    assert out.getvalue().strip() == '[TEARDOWN - FAIL] (1.50 s)'


def test_test_events(ctx):
    anon_data = DummyData()
    name_data = DummyData().with_name('new name')
    desc_data = DummyData().with_description('new description')
    full_data = DummyData().with_name('new name').with_description('new description')
    anon_test = ctx.test(DummyTest)
    anon_test.execute(anon_data)
    name_test = ctx.test(DummyTest)
    name_test.execute(name_data)
    desc_test = ctx.test(DummyTest)
    desc_test.execute(desc_data)
    full_test = ctx.test(DummyTest)
    full_test.execute(full_data)

    separator = '-' * 64

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestStartedEvent(anon_test, anon_data))
    assert out.getvalue().strip().split('\n') == [separator, '[TEST] DummyTest - Dummy Test used for testing']

    test = ctx.test(DummyTest)
    test.execute(name_data)
    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestStartedEvent(name_test, name_data))
    assert out.getvalue().strip().split('\n') == [separator, '[TEST] new name - Dummy Test used for testing']

    test = ctx.test(DummyTest)
    test.execute(desc_data)
    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestStartedEvent(desc_test, desc_data))
    assert out.getvalue().strip().split('\n') == [separator, '[TEST] DummyTest - new description']

    test = ctx.test(DummyTest)
    test.execute(full_data)
    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestStartedEvent(full_test, full_data))
    assert out.getvalue().strip().split('\n') == [separator, '[TEST] new name - new description']

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestEndedEvent(anon_test, anon_data, milliseconds(0), Status.PASS, [(None, None, None)]))
    assert out.getvalue().strip() == '[TEST - PASS] DummyTest (0 ms)'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestEndedEvent(name_test, name_data, milliseconds(-546), Status.SKIP, [(None, None, None)]))
    assert out.getvalue().strip() == '[TEST - SKIP] new name (546 ms)'

    with event_logger_context(ctx) as (publisher, out):
        publisher.notify(E.TestEndedEvent(desc_test, desc_data, milliseconds(-1001), Status.FAIL, [(None, None, None)]))
    assert out.getvalue().strip() == '[TEST - FAIL] DummyTest (1.00 s)'


def test_report_summary(ctx):
    separator = '-' * 64
    test1 = ctx.test(DummyTest)
    data1 = DummyData().with_name('test 1')
    test1.execute(data1)
    test1_iterations = [Status.PASS, Status.SKIP, Status.FAIL, Status.PASS]

    test2 = ctx.test(DummyTest)
    data2 = DummyData().with_name('test 2')
    test2.execute(data2)
    test2_iterations = [Status.FAIL, Status.FAIL, Status.SKIP, Status.PASS, Status.SKIP]

    cases = [
        {'t': test1, 'd': data1, 'i': test1_iterations, 's': Status.PASS, 'e': []},
        {'t': test2, 'd': data2, 'i': test2_iterations, 's': Status.FAIL,
         'e': [(ValueError, ValueError('oops'), TracebackBuilder()
                .with_frame('file.py', 'raise error', 4).with_frame('other.py', '5/0', 8).build()),
               (ValueError, ValueError('oops'), TracebackBuilder().with_frame('oops.py', 'raise exc', 5).build())]}
    ]

    iteration = IterationDataBuilder().with_name('My Iteration').with_description('blah blah').build()

    with event_logger_context(ctx) as (publisher, out):
        for c in cases:
            publisher.notify(E.TestStartedEvent(c['t'], c['d']))
            for i in c['i']:
                publisher.notify(E.TestIterationEndedEvent(c['t'], c['d'], iteration, milliseconds(-10), i, None))
            publisher.notify(E.TestEndedEvent(c['t'], c['d'], milliseconds(0), c['s'], c['e']))

        out.seek(0)
        out.truncate()
        publisher.notify(E.SuiteEndedEvent(ctx, milliseconds(0), Status.PASS))

    value = out.getvalue()
    print(value)
    assert value.strip().split('\n') == [
        separator, 'Execution Summary', separator, '',
        '[PASS] test 1: 4 iteration(s) (2 pass - 1 fail - 1 skip)',
        '[FAIL] test 2: 5 iteration(s) (1 pass - 2 fail - 2 skip)',
        "ValueError('oops',)",
        '  File "file.py", line 4, in raise error',
        '  File "other.py", line 8, in 5/0',
        '',
        "ValueError('oops',)",
        '  File "oops.py", line 5, in raise exc',
    ]
