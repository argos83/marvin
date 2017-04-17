import sys

from colorama import Fore, Back

import marvin.util.files
from marvin.core.status import Status
from marvin.report import EventType


COLORS = {
    Status.PASS: Fore.GREEN + '%s' + Fore.RESET,
    Status.FAIL: Fore.RED + '%s' + Fore.RESET,
    Status.SKIP: Fore.BLUE + Back.WHITE + '%s' + Back.RESET + Fore.RESET,
    'HEADER': Fore.CYAN + '%s' + Fore.RESET
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
        self._indent = "  "
        self._o = dest
        self._color = marvin.util.files.supports_color(self._o)

    def on_step_started(self, event):
        step = event.step

        self._p("-" * 64)
        self._p("%s%s: %s (%s)", self._indent * step.level, step.name, step.description, ", ".join(step.tags))

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

        self._p("-" * 64)
        self._p("[%s] %s - %s", test_header, test_script.name, status)

    def _p(self, s, *args):
        self._o.write(s % args + '\n')

    def _colored_status(self, status):
        return self._in_color(status, status)

    def _in_color(self, color, s):
        if self._color:
            return COLORS.get(color, '%s') % s
        return s
