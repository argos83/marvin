import inspect
import os
import sys


def supports_color(file_obj):
    """
    Returns True if the running system's terminal supports color, and False otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented
    is_a_tty = hasattr(file_obj, 'isatty') and file_obj.isatty()
    return supported_platform and is_a_tty


class ClassLoader(object):
    """
    Inspects the given module looking for a class member matching the given specifications
    """
    def __init__(self, parent_class, ignore_classes=None):
        self._parent = parent_class
        self._ignore = ignore_classes or []

    def find(self, mod):
        for member in mod.__dict__.values():
            if self._matches(mod, member):
                return member

    def _matches(self, mod, member):
        return (inspect.isclass(member)
                and issubclass(member, self._parent)
                and member != self._parent
                and member not in self._ignore
                and member.__module__ == mod.__name__)


class FileFinder(object):
    """
    Recursively walks a directory looking for files that satisfy the given filter
    """
    def __init__(self, search_path, filename_matcher=None):
        self._filename_matcher = filename_matcher
        self._search_path = search_path

    def find_all(self):
        for dirpath, dirnames, filenames in os.walk(self._search_path):
            for filename in filenames:
                if not self._filename_matcher or self._filename_matcher(filename):
                    yield os.path.join(dirpath, filename)

            blacklist = [dn for dn in dirnames if dn.startswith(".")]
            for dn in blacklist:
                dirnames.remove(dn)
