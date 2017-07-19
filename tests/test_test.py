import marvin
from marvin.core.status import Status
from marvin.exceptions import ContextSkippedException
from marvin.report import EventType as E
from tests.stubs import DummyTest, DummyData, DummyStep, IterationDataBuilder


ALL_TEST_EVENTS = [E.TEST_STARTED,
                   E.TEST_SETUP_STARTED, E.TEST_SETUP_ENDED,
                   E.TEST_ITERATION_STARTED, E.TEST_ITERATION_ENDED,
                   E.TEST_TEARDOWN_STARTED, E.TEST_TEARDOWN_ENDED,
                   E.TEST_ENDED]

ALL_END_EVENTS = [E.TEST_SETUP_ENDED, E.TEST_ITERATION_ENDED, E.TEST_TEARDOWN_ENDED, E.TEST_ENDED]

ALL_PHASE_START_EVENTS = [E.TEST_SETUP_STARTED, E.TEST_ITERATION_STARTED, E.TEST_TEARDOWN_STARTED]

ALL_PHASE_END_EVENTS = [E.TEST_SETUP_ENDED, E.TEST_ITERATION_ENDED, E.TEST_TEARDOWN_ENDED]


def test_test_basic(ctx):
    """Verify a basic test operation"""
    ctx.test(DummyTest).execute()


def test_test_events(ctx):
    observer = ctx.observer(*ALL_TEST_EVENTS)
    d = DummyData()
    t = ctx.test(DummyTest)
    t.execute(d)

    triggered_events = [e.event_type for e in observer.events]

    assert triggered_events == ALL_TEST_EVENTS
    assert ctx.last_reported_status == Status.PASS
    assert all(e.test_script == t for e in observer.events)
    assert all(e.data_provider == d for e in observer.events)
    assert all(e.duration == e.timestamp - e.start_time
               for e in observer.events if e.event_type in ALL_END_EVENTS)


def test_access_data_in_phase_events(ctx):
    observer = ctx.observer(*(ALL_PHASE_START_EVENTS + ALL_PHASE_END_EVENTS))
    observer.hook(lambda e: e.data['foo'].append('bar'), *ALL_PHASE_START_EVENTS)

    ctx.test(DummyTest).execute(DummyData()
                                .with_setup_data(foo=[])
                                .with_iteration(IterationDataBuilder().with_data(foo=[]).build())
                                .with_tear_down_data(foo=[]))
    assert all(e.data['foo'] == ['bar'] for e in observer.events)


def test_setup_events(ctx):
    observer = ctx.observer(E.TEST_SETUP_STARTED, E.TEST_SETUP_ENDED)
    script = ctx.test(DummyTest)
    data = DummyData().with_setup_data(fail='oops')
    script.execute(data)

    start, end = observer.events

    assert start.event_type == E.TEST_SETUP_STARTED
    assert start.data == {'fail': 'oops'}
    assert start.test_script == script
    assert start.data_provider == data
    assert start.timestamp == end.start_time

    assert end.event_type == E.TEST_SETUP_ENDED
    assert end.status == 'FAIL'
    assert end.data == {'fail': 'oops'}
    assert end.test_script == script
    assert end.data_provider == data
    assert end.duration == end.timestamp - end.start_time
    assert isinstance(end.exception[1], Exception)


def test_tear_down_events(ctx):
    observer = ctx.observer(E.TEST_TEARDOWN_STARTED, E.TEST_TEARDOWN_ENDED)
    script = ctx.test(DummyTest)
    data = DummyData().with_tear_down_data(fail='oops')
    script.execute(data)

    start, end = observer.events

    assert start.event_type == E.TEST_TEARDOWN_STARTED
    assert start.data == {'fail': 'oops'}
    assert start.test_script == script
    assert start.data_provider == data
    assert start.timestamp == end.start_time

    assert end.event_type == E.TEST_TEARDOWN_ENDED
    assert end.status == 'FAIL'
    assert end.data == {'fail': 'oops'}
    assert end.test_script == script
    assert end.data_provider == data
    assert end.duration == end.timestamp - end.start_time
    assert isinstance(end.exception[1], Exception)


def test_iteration_events(ctx):
    observer = ctx.observer(E.TEST_ITERATION_STARTED, E.TEST_ITERATION_ENDED)
    script = ctx.test(DummyTest)
    data = DummyData().with_iteration(
        IterationDataBuilder().with_name('new name')
                              .with_description('new description')
                              .with_tags('tag1', 'tag2')
                              .with_data(foo='bar')
        .build()).with_iteration(IterationDataBuilder().with_data(fail='ouch').build())
    script.execute(data)

    it1_start, it1_end, it2_start, it2_end = observer.events

    assert it1_start.event_type == E.TEST_ITERATION_STARTED
    assert it1_start.data == it1_end.data == {'foo': 'bar'}
    assert it1_start.test_script == it1_end.test_script == script
    assert it1_start.data_provider == it1_end.data_provider == data
    assert it1_start.timestamp == it1_end.start_time

    assert it1_end.event_type == E.TEST_ITERATION_ENDED
    assert it1_end.status == 'PASS'
    assert it1_end.duration == it1_end.timestamp - it1_end.start_time
    assert it1_end.exception == (None, None, None)

    assert it1_start.iteration.name == it1_end.iteration.name == 'new name'
    assert it1_start.iteration.description == it1_end.iteration.description == 'new description'
    assert it1_start.iteration.tags == it1_end.iteration.tags == {'tag1', 'tag2'}

    assert it2_start.iteration.name is None and it2_end.iteration.name is None
    assert it2_start.iteration.description is None and it2_end.iteration.description is None
    assert it2_start.iteration.tags is None and it2_end.iteration.tags is None


def test_unimplemented_methods(ctx):
    """`setup` and `tear_down` are optional but `run` is not"""
    observer = ctx.observer(E.TEST_SETUP_ENDED, E.TEST_ITERATION_ENDED,
                            E.TEST_TEARDOWN_ENDED, E.TEST_ENDED)

    class Unfinished(marvin.TestScript):
        pass

    ctx.test(Unfinished).execute()
    setup, iteration, tear_down, test = observer.events

    assert setup.status == Status.PASS
    assert iteration.status == Status.FAIL
    assert iteration.exception[0] == NotImplementedError
    assert tear_down.status == Status.PASS
    assert test.status == Status.FAIL
    assert ctx.last_reported_status == Status.FAIL


def test_fail_setup_skips_iteration_but_not_tear_down(ctx):
    observer = ctx.observer(*ALL_TEST_EVENTS)

    ctx.test(DummyTest).execute(DummyData().with_setup_data(fail='kaput'))

    triggered_events = [e.event_type for e in observer.events]
    assert triggered_events == [E.TEST_STARTED,
                                E.TEST_SETUP_STARTED, E.TEST_SETUP_ENDED,
                                E.TEST_TEARDOWN_STARTED, E.TEST_TEARDOWN_ENDED,
                                E.TEST_ENDED]

    _, _, setup, _, tear_down, test = observer.events

    assert setup.status == Status.FAIL
    assert str(setup.exception[1]) == 'kaput'
    assert tear_down.status == Status.PASS
    assert test.status == Status.FAIL
    assert test.exceptions == [setup.exception]


def test_skip_setup_skips_everything(ctx):
    observer = ctx.observer(*ALL_TEST_EVENTS)

    ctx.test(DummyTest).execute(DummyData().with_setup_data(skip='move on'))

    triggered_events = [e.event_type for e in observer.events]
    assert triggered_events == [E.TEST_STARTED,
                                E.TEST_SETUP_STARTED, E.TEST_SETUP_ENDED,
                                E.TEST_ENDED]

    _, _, setup, test = observer.events

    assert setup.status == Status.SKIP
    assert setup.exception[0] == ContextSkippedException
    assert setup.exception[1].reason == 'move on'
    assert test.status == Status.SKIP
    assert test.exceptions == [setup.exception]


def test_failed_iteration_do_not_affect_other_iterations(ctx):
    observer = ctx.observer(*ALL_END_EVENTS)

    ctx.test(DummyTest).execute(DummyData()
                                .with_iteration(IterationDataBuilder().with_data(foo='bar').build())
                                .with_iteration(IterationDataBuilder().with_data(fail='oops').build())
                                .with_iteration(IterationDataBuilder().with_data(foo='baz').build()))

    triggered_events = [e.event_type for e in observer.events]
    assert triggered_events == [E.TEST_SETUP_ENDED,
                                E.TEST_ITERATION_ENDED, E.TEST_ITERATION_ENDED, E.TEST_ITERATION_ENDED,
                                E.TEST_TEARDOWN_ENDED,
                                E.TEST_ENDED]

    setup, it1, it2, it3, tear_down, test = observer.events
    assert setup.status == Status.PASS
    assert it1.status == Status.PASS
    assert it2.status == Status.FAIL
    assert str(it2.exception[1]) == 'oops'
    assert it3.status == Status.PASS
    assert tear_down.status == Status.PASS
    assert test.status == Status.FAIL
    assert test.exceptions == [it2.exception]


def test_skip_iteration_do_not_affect_results(ctx):
    observer = ctx.observer(*ALL_END_EVENTS)

    ctx.test(DummyTest).execute(DummyData()
                                .with_iteration(IterationDataBuilder().with_data(foo='bar').build())
                                .with_iteration(IterationDataBuilder().with_data(skip='wip').build())
                                .with_iteration(IterationDataBuilder().with_data(foo='baz').build()))

    triggered_events = [e.event_type for e in observer.events]
    assert triggered_events == [E.TEST_SETUP_ENDED,
                                E.TEST_ITERATION_ENDED, E.TEST_ITERATION_ENDED, E.TEST_ITERATION_ENDED,
                                E.TEST_TEARDOWN_ENDED,
                                E.TEST_ENDED]

    setup, it1, it2, it3, tear_down, test = observer.events
    assert setup.status == Status.PASS
    assert it1.status == Status.PASS
    assert it2.status == Status.SKIP
    assert it2.exception[1].reason == 'wip'
    assert it3.status == Status.PASS
    assert tear_down.status == Status.PASS
    assert test.status == Status.PASS
    assert test.exceptions == [it2.exception]


def test_tests_are_reportable(ctx):
    """TestScripts inherit the capabilities from the Reportable MixIn"""

    # See test_reportable.py to understand the whole set of capabilities

    class SimpleTest(marvin.TestScript):
        """Test description"""
        TAGS = ['a', 'few', 'tags']

        def run(self, data):
            self.tag('and', 'magic')
            self.untag('a', 'few')

    test = ctx.test(SimpleTest)
    test.execute()

    assert test.name == 'SimpleTest'
    assert test.description == 'Test description'
    assert test.tags == {'tags', 'and', 'magic'}


def test_test_meta_extended_from_data(ctx):
    class SimpleTest(marvin.TestScript):
        """Test description"""
        TAGS = ['a', 'few', 'tags']

    test = ctx.test(SimpleTest)
    test.execute(DummyData()
                 .with_name('New Name')
                 .with_description('New description')
                 .wih_tags('more', 'tags', 4))

    assert test.name == 'New Name'
    assert test.description == 'New description'
    assert test.tags == {'a', 'few', 'tags', 'more', '4'}


def test_can_run_steps(ctx):
    observer = ctx.observer(E.STEP_ENDED)

    class SimpleTest(marvin.TestScript):
        def run(self, data):
            self.step(DummyStep).execute()

    ctx.test(SimpleTest).execute()
    assert observer.last_event.step.name == 'DummyStep'


def test_has_access_to_config(ctx):
    ctx.cfg.set('answer', 40)

    class SimpleTest(marvin.TestScript):
        def run(self, data):
            self.cfg.set('answer', self.cfg.answer + 1)
            with self.step(DummyStep).do() as (step, _result):
                step.cfg.set('answer', step.cfg.answer + 1)

    ctx.test(SimpleTest).execute()
    assert ctx.cfg.answer == 42
