"""Events that happen inside Marvin"""


class Events(object):
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
