from marvin import TestScript

from steps.check_website_title import CheckWebsiteTitle


class WebsiteTitles(TestScript):
    """Checks website titles"""
    NAME = "Website Titles"
    TAGS = ["web", "title"]

    def setup(self, data):
        pass

    def run(self, data):
        self.step(CheckWebsiteTitle).execute(data["website"], data["expected_title"])

    def tear_down(self, _data):
        # Clean up / logout, etc
        pass
