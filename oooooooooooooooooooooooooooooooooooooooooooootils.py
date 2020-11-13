import os
import sys

def darken(value, amt = 60):
    return max(value - amt, 0)


def lighten(value, amt  = 60):
    return min(value + amt, 255)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path) 
