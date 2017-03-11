import time
import urllib2
import json
from datetime import datetime

from marvin import Publisher
from marvin import Events


class ELKReporter(object):

    def __init__(self, base_url, index, schema_type="marvin"):
        Publisher.subscribe(Events.STEP_ENDED, self.on_step_ended)
        Publisher.subscribe(Events.TEST_STARTED, self.on_test_started)
        Publisher.subscribe(Events.TEST_ENDED, self.on_test_ended)
        Publisher.subscribe(Events.SUITE_ENDED, self.on_suite_ended)
        self.tests = []
        self._current_test = None
        self._base_url = base_url
        self._index = index
        self._type = schema_type

    def on_test_started(self, _event, data):
        test_script = data['test_script']

        self._current_test = {
            "name": test_script.name,
            "description": test_script.description,
            "tags": test_script.tags,
            "steps": []
        }

    def on_test_ended(self, _event, data):
        self._current_test["status"] = data['status']
        self._current_test["timestamp"] = self._ms_to_iso(data['timestamp'])
        self._current_test["duration"] = data['timestamp'] - data['start_time']
        self.tests.append(self._current_test)

    def on_step_ended(self, _event, data):
        step = data['step']
        step_info = {
            "name": step.name,
            "description": step.description,
            "tags": step.tags,
            "status": data['status'],
            "timestamp": self._ms_to_iso(data['timestamp']),
            "duration": data['timestamp'] - data['start_time']
        }
        self._current_test['steps'].append(step_info)

    def on_suite_ended(self, _event, _data):
        self._publish()

    def _publish(self):
        url = self._base_url + self._index + '/' + self._type
        data = json.dumps({"tests": self.tests, "timestamp": self._ms_to_iso(time.time() * 1000.0)})

        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        urllib2.urlopen(req)

    def _ms_to_iso(self, milliseconds):
        return datetime.fromtimestamp(milliseconds/1000.0).isoformat()
