from colorama import Fore

from marvin import Publisher
from marvin import Events

class EventLogger(object):

    def __init__(self):
        Publisher.subscribe(Events.STEP_STARTED, self.on_step_started)
        Publisher.subscribe(Events.STEP_ENDED, self.on_step_ended)
        Publisher.subscribe(Events.TEST_STARTED, self.on_test_started)
        Publisher.subscribe(Events.TEST_ENDED, self.on_test_ended)
        self._level = 0
        self._indent = "  "

    def on_step_started(self, _event, data):
        self._level += 1
        step = data['step']

        print "%s%s: %s (%s)" % (self._indent * self._level, step.name, step.description, ", ".join(step.tags))
        print "----------------------------------------------------------------"

    def on_step_ended(self, _event, data):
        step = data['step']
        duration = data['timestamp'] - data['start_time']

        status = data['status']
        if status == 'PASSED':
            status = Fore.GREEN + status + Fore.RESET
        elif status == 'FAILED':
            status = Fore.RED + status + Fore.RESET

        print "%s[%s] %s (%d ms)" % (self._indent * self._level, status, step.name, duration)
        self._level -= 1

    def on_test_started(self, _event, data):
        test_script = data['test_script']

        test_header = Fore.CYAN + 'TEST' + Fore.RESET

        print "[%s] %s - %s" % (
            test_header, test_script.name, test_script.description
        )


    def on_test_ended(self, _event, data):
        test_script = data['test_script']

        test_header = Fore.CYAN + 'TEST' + Fore.RESET

        status = data['status']
        if status == 'PASSED':
            status = Fore.GREEN + status + Fore.RESET
        elif status == 'FAILED':
            status = Fore.RED + status + Fore.RESET

        print "[%s] %s - %s" % (test_header, test_script.name, status)

