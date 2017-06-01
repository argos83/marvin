import sys

IS_PYTHON_3 = sys.version_info >= (3, 0)
IS_PYTHON_2 = sys.version_info[0] == 2


def raise_exc_info(_exc_type, exc_val, exc_tb):
    if IS_PYTHON_3:
        return exc_val.with_traceback(exc_tb)
    return exc_val, None, exc_tb


def import_module(module_path, module_name):
    if sys.version_info >= (3, 5):
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    elif sys.version_info >= (3, 3):
        from importlib.machinery import SourceFileLoader
        mod = SourceFileLoader(module_name, module_path).load_module()

    elif IS_PYTHON_2:
        import imp
        mod = imp.load_source(module_name, module_path)
    else:
        raise RuntimeError("Python version not supported: %s" % (".".join(sys.version_info)))

    return mod


def urllib_mod():
    if IS_PYTHON_3:
        import urllib.request
        return urllib.request
    else:
        import urllib2
        return urllib2
