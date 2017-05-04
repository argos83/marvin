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
    'BLOCK': Fore.MAGENTA + '%s' + Fore.RESET
}

INDENT_CHAR = " "


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
        publisher.subscribe(self.on_setup_started, EventType.TEST_SETUP_STARTED)
        publisher.subscribe(self.on_setup_ended, EventType.TEST_SETUP_ENDED)
        publisher.subscribe(self.on_iteration_started, EventType.TEST_ITERATION_STARTED)
        publisher.subscribe(self.on_iteration_ended, EventType.TEST_ITERATION_ENDED)
        publisher.subscribe(self.on_teardown_started, EventType.TEST_TEARDOWN_STARTED)
        publisher.subscribe(self.on_teardown_ended, EventType.TEST_TEARDOWN_ENDED)
        publisher.subscribe(self.on_suite_ended, EventType.SUITE_ENDED)

        self._indent = INDENT_CHAR * 2
        self._o = dest
        self._color = marvin.util.files.supports_color(self._o)
        self._iterations_status = {

        }
        self._suite_status = []

    def on_setup_started(self, event):
        self._suite_status.append({
            "test_name": event.test_script.name,
            "test_status": None,
            "iterations": {
                Status.PASS: 0,
                Status.FAIL: 0,
                Status.SKIP: 0
            }
        })
        self._on_block_started('SETUP STARTED')

    def on_setup_ended(self, event):
        self._on_block_ended(event, 'SETUP FINISHED')

    def on_iteration_started(self, event):
        self._on_block_started('ITERATION STARTED')

    def on_iteration_ended(self, event):
        test_object = self._get_suite_status_item(event.test_script.name)
        test_object["iterations"][event.status] += 1
        #self._iterations_status[event.status] += 1
        self._on_block_ended(event, 'ITERATION FINISHED')

    def on_teardown_started(self, event):
        self._on_block_started('TEARDOWN STARTED')

    def on_teardown_ended(self, event):
        self._on_block_ended(event, 'TEARDOWN FINISHED')

    def _on_block_started(self, title):
        block_header = self._in_color('BLOCK', title)
        self._indent = INDENT_CHAR * 4
        self._p("%s[%s]", self._indent, block_header)

    def _on_block_ended(self, event, title):
        block_header = self._in_color('BLOCK', title)
        status = self._colored_status(event.status)
        self._p("%s[%s - %s]", self._indent, block_header, status)
        self._indent = INDENT_CHAR * 2

    def on_step_started(self, event):
        step = event.step
        tags = "(" + ", ".join(step.tags) + (")") if len(step.tags) > 0 else ""

        self._p("-" * 64)
        self._p("%s%s: %s %s", self._indent * step.level, step.name, step.description, tags)

    def on_step_ended(self, event):
        step = event.step
        status = self._colored_status(event.status)

        self._p("%s[%s] %s (%d ms)", self._indent * step.level, status, step.name, event.duration)

    def on_test_started(self, event):
        test_script = event.test_script
        test_header = self._in_color('HEADER', 'TEST')

        self._p("[%s] %s - %s", test_header, test_script.name, test_script.description)

    def on_test_ended(self, event):
        test_script = event.test_script
        test_header = self._in_color('HEADER', 'TEST')
        status = self._colored_status(event.status)
        test_object = self._get_suite_status_item(test_script.name)
        test_object["test_status"] = event.status

        if event.status != Status.PASS:
            exception = event.exceptions[0]
            self._p(repr(exception[1]))
            self._p(''.join(traceback.format_tb(exception[2])))

        self._p("-" * 64)
        self._p("[%s] %s - %s", test_header, test_script.name, status)

    def on_suite_ended(self, event):
        self._p("\n" + "-" * 64)
        self._p("Execution Summary")
        self._p("-" * 64)
        for test in self._suite_status:
            status = self._colored_status(test["test_status"])
            self._p("\n%s - %s", test["test_name"], status)
            for status, value in test["iterations"].iteritems():
                self._p("%s%s: %i", self._indent, status, value)

    def _p(self, s, *args):
        self._o.write(s % args + "\n")

    def _colored_status(self, status):
        return self._in_color(status, status)

    def _in_color(self, color, s):
        if self._color:
            return COLORS.get(color, "%s") % s
        return s

    def _get_suite_status_item(self, test_name):
        for item in self._suite_status:
            if item["test_name"] == test_name:
                test_status = item
                break
        else:
            test_status = None

        return test_status
