import sys
import traceback

from colorama import Fore, Back

import marvin.util.files
from marvin.core.status import Status
from marvin.report import EventType


COLORS = {
    Status.PASS: Fore.GREEN + '%s' + Fore.RESET,
    Status.FAIL: Fore.RED + '%s' + Fore.RESET,
    Status.SKIP: Fore.BLUE + Back.WHITE + '%s' + Back.RESET + Fore.RESET,
    'HEADER': Fore.CYAN + '%s' + Fore.RESET,
    'PHASE': Fore.MAGENTA + '%s' + Fore.RESET
}

INDENT = "  "

PHASE_TITLES = {
    EventType.TEST_SETUP_STARTED: "SETUP STARTED",
    EventType.TEST_SETUP_ENDED: "SETUP ENDED",
    EventType.TEST_ITERATION_STARTED: "ITERATION STARTED",
    EventType.TEST_ITERATION_ENDED: "ITERATION ENDED",
    EventType.TEST_TEARDOWN_STARTED: "TEARDOWN STARTED",
    EventType.TEST_TEARDOWN_ENDED: "TEARDOWN ENDED"
}


class EventLogger(object):
    """
    Prints the summary of test execution results in a terminal or file
    """

    def __init__(self, publisher, dest=sys.stdout):
        """
        Builds and subscribes an EventLogger
        :param publisher: The context's publisher instance
        :param dest: The output destination (defaults to sys.stdout)
        """
        publisher.subscribe(self.on_step_started, EventType.STEP_STARTED)
        publisher.subscribe(self.on_step_ended, EventType.STEP_ENDED)
        publisher.subscribe(self.on_test_started, EventType.TEST_STARTED)
        publisher.subscribe(self.on_test_ended, EventType.TEST_ENDED)
        publisher.subscribe(self.on_phase_started,
                            EventType.TEST_SETUP_STARTED,
                            EventType.TEST_ITERATION_STARTED,
                            EventType.TEST_TEARDOWN_STARTED)
        publisher.subscribe(self.on_phase_ended,
                            EventType.TEST_SETUP_ENDED,
                            EventType.TEST_ITERATION_ENDED,
                            EventType.TEST_TEARDOWN_ENDED)
        publisher.subscribe(self.collect_iteration_status, EventType.TEST_ITERATION_ENDED)
        publisher.subscribe(self.on_suite_ended, EventType.SUITE_ENDED)

        self._o = dest
        self._color = marvin.util.files.supports_color(self._o)
        self._suite_status = []
        self._current_status = {}

    def collect_iteration_status(self, event):
        self._current_status["iterations"][event.status] += 1

    def on_phase_started(self, event):
        title = PHASE_TITLES[event.event_type]
        phase_header = self._in_color('PHASE', title)
        self._p("%s[%s]", INDENT, phase_header)

    def on_phase_ended(self, event):
        title = PHASE_TITLES[event.event_type]
        phase_header = self._in_color('PHASE', title)
        status = self._colored_status(event.status)
        self._p("%s[%s - %s]", INDENT, phase_header, status)

    def on_step_started(self, event):
        step = event.step
        tags = "(" + ", ".join(step.tags) + ")" if step.tags else ""
        indent = INDENT * step.level
        self._p(indent + "-" * 64)
        self._p("%s%s: %s %s", indent, step.name, step.description, tags)

    def on_step_ended(self, event):
        step = event.step
        status = self._colored_status(event.status)

        self._p("%s[%s] %s (%d ms)", INDENT * step.level, status, step.name, event.duration)

    def on_test_started(self, event):
        test_name = event.test_script.name

        self._current_status = {
            "test_name": test_name,
            "test_status": None,
            "iterations": {
                Status.PASS: 0,
                Status.FAIL: 0,
                Status.SKIP: 0
            }
        }
        test_script = event.test_script
        test_header = self._in_color('HEADER', 'TEST')
        self._p("-" * 64)
        self._p("[%s] %s - %s", test_header, test_script.name, test_script.description)

    def on_test_ended(self, event):
        test_script = event.test_script
        test_header = self._in_color('HEADER', 'TEST')
        status = self._colored_status(event.status)
        self._current_status["test_status"] = event.status

        self._suite_status.append(self._current_status)

        if event.status != Status.PASS and any(event.exceptions):
            exception = event.exceptions[0]
            self._p(repr(exception[1]))
            self._p(''.join(traceback.format_tb(exception[2])))

        self._p("[%s] %s - %s", test_header, test_script.name, status)

    def on_suite_ended(self, event):
        self._p("\n" + "-" * 64)
        self._p("Execution Summary")
        self._p("-" * 64 + "\n")
        for test in self._suite_status:
            status = self._colored_status(test["test_status"])
            ipass = test["iterations"][Status.PASS]
            ifail = test["iterations"][Status.FAIL]
            iskip = test["iterations"][Status.SKIP]
            iall = ipass + ifail + iskip
            iteration_summary = "%d iteration(s) (%d pass - %d fail - %d skip)" % (iall, ipass, ifail, iskip)
            self._p("[%s] %s: %s", status, test["test_name"], iteration_summary)

    def _p(self, s, *args):
        self._o.write(s % args + "\n")

    def _colored_status(self, status):
        return self._in_color(status, status)

    def _in_color(self, color, s):
        if self._color:
            return COLORS.get(color, "%s") % s
        return s
