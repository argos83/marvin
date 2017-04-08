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
