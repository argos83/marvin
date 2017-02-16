import json

from marvin.data.data_provider import DataProvider

class JSONDataProvider(DataProvider):
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
    
    def __init__(self, *args, **kargs):
        super(JSONData, self).__init__(*args, **kargs)
        with open(self._source_id, "r") as fd:
            self.json = json.load(fd)

    def setup_data(self):
        return self.json.get('setup', {})

    # GENERATOR
    def iteration_data(self):
        for it_data in self.json.get('iterations', []):
            yield it_data

    def tear_down_data(self):
        return self.json.get('tear_down', {})