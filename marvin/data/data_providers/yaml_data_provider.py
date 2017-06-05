"""YAML Data Provider"""

import yaml

from marvin.data.file_data_provider import FileDataProvider


class YAMLDataProvider(FileDataProvider):
    """
    DataDriven data provider for YAML/JSON sources.
    The data_source_id of this provider is the path to:
     * a YAML file with the following structure:
        ---
        setup:
            any: data
        iterations:
            - some: data
              for_iteration: 1
            - another: iteration
              with: more data
        tear_down:
            data_for: tear down

     * or a JSON file with the equivalent representation:
        {
          "setup": {"any": "data"},
          "iterations": [
            {"some": "data", "for_iteration": 1},
            {"another": "iteration", "with": "more data"},
          ],
          "tear_down": {"data_for": "tear down"}
        }
    """

    @classmethod
    def load_obj(cls, file_handle):
        return yaml.load(file_handle)

    @classmethod
    def supported_extensions(cls):
        return ['yml', 'yaml', 'json']
