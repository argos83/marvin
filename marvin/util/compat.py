import sys

IS_PYTHON_3 = sys.version_info >= (3, 0)


def raise_exc_info(_exc_type, exc_val, exc_tb):
    if IS_PYTHON_3:
        return exc_val.with_traceback(exc_tb)
    return exc_val, None, exc_tb


def urllib_mod():
    if IS_PYTHON_3:
        import urllib.request
        return urllib.request
    else:
        import urllib2
        return urllib2
