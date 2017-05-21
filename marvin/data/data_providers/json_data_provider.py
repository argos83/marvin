"""JSON Data Provider"""

import json

from marvin.data.file_data_provider import FileDataProvider


class JSONDataProvider(FileDataProvider):
    """
    DataDriven data provider for JSON sources.
    The data_source_id of this provider is the path to a JSON file with the following structure:

        {
          "setup": *** JSON object representing data for the 'setup' block ***,
          "iterations": [
            *** JSON object representing data for iteration 1 ('run' block) ***,
            *** JSON object representing data for iteration 2 ('run' block) ***,
            ...,
            *** JSON object representing data for iteration N ('run' block) ***,
          ],

          "tear_down": *** JSON object representing data for the 'tear_down' block ***
        }
    """

    @classmethod
    def load_obj(cls, file_handle):
        return json.load(file_handle)

    @classmethod
    def supported_extensions(cls):
        return ['json']
