import keyword
import os.path
import yaml


class Config(object):

    def __init__(self):
        self._data = {}

    def load(self, *config_files):
        for config_file in config_files:
            self.load_into(None, config_file)

    def load_into(self, namespace, config_file):
        name, ext = os.path.splitext(os.path.basename(config_file))
        with open(config_file) as fh:
            value = self._load_file(fh, ext.lower())
        self.set(namespace or name, value)

    def _load_file(self, fh, file_type):
        if file_type in ['.yaml', '.yml', '.json']:
            return yaml.load(fh)
        else:
            raise ValueError("Unsupported config extension: '%s'" % file_type)

    def set(self, name, obj):
        if keyword.iskeyword(name):
            raise ValueError("Can't use reserved name '%s' as config item" % name)
        self._data[name] = self._deep_merge(self._data.get(name), obj)

    def _deep_merge(self, base, update):
        if not (isinstance(base, dict) and isinstance(update, dict)):
            return update

        for key in update:
            if key in base and base[key] != update[key]:
                base[key] = self._deep_merge(base[key], update[key])
            else:
                base[key] = update[key]
        return base

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError("Config setting '%s' not set" % name)
