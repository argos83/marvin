from marvin.report import EventType


def main(publisher, cfg):
    CustomLogger(publisher, cfg)


class CustomLogger(object):
    def __init__(self, publisher, cfg):
        publisher.subscribe(self.on_test_started, EventType.TEST_STARTED)
        publisher.subscribe(self.on_test_ended, EventType.TEST_ENDED)

    def on_test_started(self, event):
        print("#### CUSTOM LOGGER - TEST STARTING ####")

    def on_test_ended(self, event):
        print("#### CUSTOM LOGGER- TEST ENDING ####")
