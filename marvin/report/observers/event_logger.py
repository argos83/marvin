import sys
import traceback

from colorama import Fore

import marvin.util.files
from marvin.core.status import Status
from marvin.report import EventType as E
from marvin.exceptions import ContextSkippedException


COLORS = {
    Status.PASS: Fore.GREEN + '%s' + Fore.RESET,
    Status.FAIL: Fore.RED + '%s' + Fore.RESET,
    Status.SKIP: Fore.YELLOW + '%s' + Fore.RESET,
    'HEADER': Fore.CYAN + '%s' + Fore.RESET,
    'PHASE': Fore.MAGENTA + '%s' + Fore.RESET
}

INDENT = "  "

PHASE_TITLES = {
    E.TEST_SETUP_STARTED: "SETUP",
    E.TEST_SETUP_ENDED: "SETUP",
    E.TEST_ITERATION_STARTED: "ITERATION",
    E.TEST_ITERATION_ENDED: "ITERATION",
    E.TEST_TEARDOWN_STARTED: "TEARDOWN",
    E.TEST_TEARDOWN_ENDED: "TEARDOWN"
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
        publisher.subscribe(self.on_step_started, E.STEP_STARTED)
        publisher.subscribe(self.on_step_ended, E.STEP_ENDED)
        publisher.subscribe(self.on_test_started, E.TEST_STARTED)
        publisher.subscribe(self.on_test_ended, E.TEST_ENDED)
        publisher.subscribe(self.on_phase_started,
                            E.TEST_SETUP_STARTED,
                            E.TEST_ITERATION_STARTED,
                            E.TEST_TEARDOWN_STARTED)
        publisher.subscribe(self.on_phase_ended,
                            E.TEST_SETUP_ENDED,
                            E.TEST_ITERATION_ENDED,
                            E.TEST_TEARDOWN_ENDED)
        publisher.subscribe(self.collect_iteration_status, E.TEST_ITERATION_ENDED)
        publisher.subscribe(self.on_suite_ended, E.SUITE_ENDED)

        self._o = dest
        self._color = marvin.util.files.supports_color(self._o)
        self._suite_status = []
        self._reset_test_summary()

    def collect_iteration_status(self, event):
        self._current_test["iterations"][event.status] += 1

    def on_phase_started(self, event):
        title = PHASE_TITLES[event.event_type]
        phase_header = self._in_color('PHASE', title)
        phase_suffix = self._get_phase_suffix(event)
        self._p("%s[%s]%s", INDENT, phase_header, phase_suffix)

    def on_phase_ended(self, event):
        title = PHASE_TITLES[event.event_type]
        phase_header = self._in_color('PHASE', title)
        phase_suffix = self._get_phase_suffix(event)
        status = self._colored_status(event.status)
        self._p("%s[%s - %s]%s (%s)", INDENT, phase_header, status, phase_suffix, self._format_duration(event.duration))

    def on_step_started(self, event):
        step = event.step
        indent = INDENT * step.level
        self._p("%s%s: %s", indent, step.name, step.description)

    def on_step_ended(self, event):
        step = event.step
        status = self._colored_status(event.status)
        indent = INDENT * step.level
        self._p("%s[%s] %s (%s)", indent, status, step.name, self._format_duration(event.duration))

        if event.status == Status.SKIP and event.exception[0] == ContextSkippedException:
            self._p("%sSkip reason: %s", indent, event.exception[1].reason)
        elif event.status != Status.PASS and event.exception[2]:
            self._p("%s", self._format_exception(event.exception))

    def on_test_started(self, event):
        test_script = event.test_script
        self._reset_test_summary(test_script.name)
        test_header = self._in_color('HEADER', 'TEST')
        self._p("-" * 64)
        self._p("[%s] %s - %s", test_header, test_script.name, test_script.description)

    def _format_exception(self, exc_info):
        return "%s\n%s" % (repr(exc_info[1]), ''.join(traceback.format_tb(exc_info[2])))

    def on_test_ended(self, event):
        test_script = event.test_script
        test_header = self._in_color('HEADER', 'TEST')
        status = self._colored_status(event.status)
        self._current_test["status"] = event.status

        self._suite_status.append(self._current_test)
        if event.status != Status.PASS:
            for exc_info in event.exceptions:
                self._current_test["exceptions"].append(self._format_exception(exc_info))
        self._p("[%s - %s] %s (%s)", test_header, status, test_script.name, self._format_duration(event.duration))

    def on_suite_ended(self, event):
        self._p("\n" + "-" * 64)
        self._p("Execution Summary")
        self._p("-" * 64 + "\n")
        for test in self._suite_status:
            status = self._colored_status(test['status'])
            ipass = test['iterations'][Status.PASS]
            ifail = test['iterations'][Status.FAIL]
            iskip = test['iterations'][Status.SKIP]
            iall = ipass + ifail + iskip
            iteration_summary = "%d iteration(s) (%d pass - %d fail - %d skip)" % (iall, ipass, ifail, iskip)
            self._p("[%s] %s: %s", status, test['name'], iteration_summary)
            [self._p("%s", exception) for exception in test['exceptions']]

    def _get_phase_suffix(self, event):
        suffix = ""
        if event.event_type in (E.TEST_ITERATION_STARTED, E.TEST_ITERATION_ENDED) and event.iteration.name:
            suffix += ' ' + event.iteration.name
        if event.event_type == E.TEST_ITERATION_STARTED and event.iteration.description:
            suffix += ': ' + event.iteration.description
        return suffix

    def _reset_test_summary(self, test_name=None):
        self._current_test = {
            "name": test_name,
            "status": None,
            "exceptions": [],
            "iterations": {
                Status.PASS: 0,
                Status.FAIL: 0,
                Status.SKIP: 0
            }
        }

    def _p(self, s, *args):
        self._o.write(s % args + "\n")

    def _colored_status(self, status):
        return self._in_color(status, status)

    def _format_duration(self, millis):
        if millis < 1000:
            return "%d ms" % millis
        return "%.2f s" % (millis/1000.0)

    def _in_color(self, color, s):
        if self._color:
            return COLORS.get(color, "%s") % s
        return s
