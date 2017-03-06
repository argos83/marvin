from marvin.report import EventType


class Publisher(object):

    def __init__(self):
        self._observers = {}
        
    def subscribe(self, observer, *event_types):
        for event_type in event_types:
            self._observers.setdefault(event_type, []).append(observer)

    def subscribe_all(self, observer):
        self.subscribe(observer, *EventType.ALL)

    def notify(self, event):
        for observer in self._observers.get(event.event_type, []):
            observer(event)
