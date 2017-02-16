from events import Events

class _Publisher(object):

    def __init__(self):
        self._observers = {}
        for event in Events.ALL:
            self._observers[event] = []
        
    def subscribe(self, event, observer):
        self._observers[event].append(observer)

    def subscribe_all(self, observer):
        for event in Events.ALL:
            self.subscribe(event, observer)

    def notify(self, event, data):
        for observer in self._observers[event]:
            observer(event, data)

Publisher = _Publisher()