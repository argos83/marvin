from marvin import Step

import requests
import bs4

class CheckWebsiteTitle(Step):

    NAME = "Check Website Title"
    DESCRIPTION = "Checks if a website has an expected title"

    def run(self, website, expected_title):
        response = requests.get(website)
        html = bs4.BeautifulSoup(response.text, "html.parser")
        real_title = html.title.text
        if real_title != expected_title:
            raise Exception(
                "Title '%s' is not equal to expected '%s'"
                % (expected_title, real_title)
            )

        return real_title
