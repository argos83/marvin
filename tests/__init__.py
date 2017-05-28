import contextlib
import os


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
