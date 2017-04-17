from marvin import Step

import requests
import bs4


class CheckWebsiteTitle(Step):
    """Checks if a website has an expected title"""

    NAME = "Check Website Title"

    def run(self, website, expected_title):

        if expected_title == "Google":
            self.skip("Skipping test")

        response = requests.get(website)
        html = bs4.BeautifulSoup(response.text, "html.parser")
        real_title = html.title.text

        assert real_title == expected_title,\
            "Title '%s' is not equal to expected '%s'" % (expected_title, real_title)

        return real_title
