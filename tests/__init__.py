import os.path


def resource(path):
    here = os.path.dirname(__file__)
    return os.path.join(here, 'resources', path)
