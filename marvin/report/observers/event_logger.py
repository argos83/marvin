from colorama import Fore, Back

from marvin.core.status import Status
from marvin.report import EventType


class EventLogger(object):

    def __init__(self, publisher):
        publisher.subscribe(self.on_step_started, EventType.STEP_STARTED)
        publisher.subscribe(self.on_step_ended, EventType.STEP_ENDED)
        publisher.subscribe(self.on_test_started, EventType.TEST_STARTED)
        publisher.subscribe(self.on_test_ended, EventType.TEST_ENDED)
        self._indent = "  "

    def on_step_started(self, event):
        step = event.step

        print("----------------------------------------------------------------")
        print("%s%s: %s (%s)" % (self._indent * step.level, step.name, step.description, ", ".join(step.tags)))

    def on_step_ended(self, event):
        step = event.step
        status = self._colored_status(event.status)

        print("%s[%s] %s (%d ms)" % (self._indent * step.level, status, step.name, event.duration))

    def on_test_started(self, event):
        test_script = event.test_script
        test_header = Fore.CYAN + 'TEST' + Fore.RESET

        print("[%s] %s - %s" % (test_header, test_script.name, test_script.description))

    def on_test_ended(self, event):
        test_script = event.test_script
        test_header = Fore.CYAN + 'TEST' + Fore.RESET
        status = self._colored_status(event.status)

        print("----------------------------------------------------------------")
        print("[%s] %s - %s" % (test_header, test_script.name, status))

    def _colored_status(self, status):
        if status == Status.PASS:
            return Fore.GREEN + status + Fore.RESET
        elif status == Status.FAIL:
            return Fore.RED + status + Fore.RESET
        elif status == Status.SKIP:
            return Fore.BLUE + Back.WHITE + status + Back.RESET + Fore.RESET
        return status
