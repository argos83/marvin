import pytest

import marvin
from marvin.core.status import Status
from marvin.report import EventType as E
from tests.stubs import DummyTest, DummySuite, DummyData


def test_suite_events():
    suite = DummySuite()

    observer = suite.observer(E.SUITE_STARTED, E.SUITE_ENDED)
    suite.add_test(DummyTest)
    suite.execute()

    triggered_events = [e.event_type for e in observer.events]

    assert triggered_events == [E.SUITE_STARTED, E.SUITE_ENDED]
    end_event = observer.last_event
    assert end_event.status == Status.PASS
    assert end_event.duration == end_event.timestamp - end_event.start_time
    assert all(e.suite == suite for e in observer.events)


def test_unimplemented_methods():
    """method `tests` must be implemented"""

    class Unfinished(marvin.Suite):
        pass

    suite = Unfinished()
    with pytest.raises(NotImplementedError):
        suite.execute()


def test_skip_exceptions_not_skipping_suite():
    suite = DummySuite()
    observer = suite.observer(E.TEST_ENDED, E.SUITE_ENDED)

    suite.add_test(DummyTest)
    suite.add_test(DummyTest, DummyData()
                   .with_setup(skip='skipped'))
    suite.add_test(DummyTest, DummyData()
                   .with_iteration()
                   .with_iteration(skip='skipped')
                   .with_iteration())
    suite.add_test(DummyTest)

    suite.execute()
    triggered_events = [e.event_type for e in observer.events]
    assert triggered_events == [E.TEST_ENDED] * 4 + [E.SUITE_ENDED]
    assert [e.status for e in observer.events] == [Status.PASS, Status.SKIP, Status.PASS, Status.PASS, Status.PASS]


def test_suite_status_skip_if_no_tests():
    suite = DummySuite()
    observer = suite.observer(E.SUITE_ENDED)
    suite.execute()

    end_event = observer.last_event

    assert end_event.status == Status.SKIP


def test_suite_status_skip_if_all_tests_skipped():
    suite = DummySuite()
    observer = suite.observer(E.SUITE_ENDED)

    suite.add_test(DummyTest, DummyData()
                   .with_setup(skip='skipped'))
    suite.add_test(DummyTest, DummyData()
                   .with_setup(skip='skipped'))
    suite.execute()
    end_event = observer.last_event
    assert end_event.status == Status.SKIP


def test_suite_status_fail_if_one_test_fails():
    suite = DummySuite()
    observer = suite.observer(E.TEST_ENDED, E.SUITE_ENDED)

    suite.add_test(DummyTest)  # passes
    suite.add_test(DummyTest, DummyData().with_setup(skip='skipped'))  # skipped
    suite.add_test(DummyTest, DummyData().with_iteration(fail='oops'))  # fails
    suite.add_test(DummyTest)  # passes
    suite.execute()

    assert [e.status for e in observer.events] == [Status.PASS, Status.SKIP, Status.FAIL, Status.PASS, Status.FAIL]
