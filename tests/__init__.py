import contextlib
import os
import sys

from marvin.util import compat


def resource(path):
    here = os.path.dirname(__file__)
    return os.path.join(here, 'resources', path)


@contextlib.contextmanager
def env_var(name, value):
    exists = name in os.environ
    old_value = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if not exists:
            os.environ.pop(name)
        else:
            os.environ[name] = old_value


class CaptureOutput(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = compat.string_io()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout
