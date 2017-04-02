from test_cases.website_titles import WebsiteTitles

from marvin.data.data_providers.json_data_provider import JSONDataProvider
from marvin.report.observers.event_logger import EventLogger
from marvin import Suite


class WebsiteTitlesSuite(Suite):

    def tests(self):
        return [
            (WebsiteTitles, JSONDataProvider("test_cases/website_title.json"))
        ]


if __name__ == '__main__':
    suite = WebsiteTitlesSuite()
    EventLogger(suite.publisher)
    suite.execute()
