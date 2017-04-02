import time
import json
from datetime import datetime

from marvin.report import EventType
from marvin.util.compat import urllib_mod


class ELKReporter(object):

    def __init__(self, publisher, base_url, index, schema_type="marvin"):
        publisher.subscribe(self.on_step_ended, EventType.STEP_ENDED)
        publisher.subscribe(self.on_test_started, EventType.TEST_STARTED)
        publisher.subscribe(self.on_test_ended, EventType.TEST_ENDED)
        publisher.subscribe(self.on_suite_ended, EventType.SUITE_ENDED)
        self.tests = []
        self._current_test = None
        self._base_url = base_url
        self._index = index
        self._type = schema_type

    def on_test_started(self, event):
        test_script = event.test_script

        self._current_test = {
            "name": test_script.name,
            "description": test_script.description,
            "tags": test_script.tags,
            "steps": []
        }

    def on_test_ended(self, event):
        self._current_test["status"] = event.status
        self._current_test["timestamp"] = self._ms_to_iso(event.timestamp)
        self._current_test["duration"] = event.duration
        self.tests.append(self._current_test)

    def on_step_ended(self, event):
        step = event.step
        step_info = {
            "name": step.name,
            "description": step.description,
            "tags": step.tags,
            "status": event.status,
            "timestamp": self._ms_to_iso(event.timestamp),
            "duration": event.duration
        }
        self._current_test['steps'].append(step_info)

    def on_suite_ended(self, _event):
        self._publish()

    def _publish(self):
        url = self._base_url + self._index + '/' + self._type
        data = json.dumps({"tests": self.tests, "timestamp": self._ms_to_iso(time.time() * 1000)})
        urllib = urllib_mod()
        req = urllib.Request(url, data, {'Content-Type': 'application/json'})
        urllib.urlopen(req)

    def _ms_to_iso(self, milliseconds):
        return datetime.fromtimestamp(milliseconds/1000.0).isoformat()
