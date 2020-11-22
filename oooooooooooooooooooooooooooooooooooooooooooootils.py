import os
import sys
import pathlib
import pypresence

def darken(value, amt = 60):
    return max(value - amt, 0)


def lighten(value, amt  = 60):
    return min(value + amt, 255)



# whether this is a mac pyinstaller build or not
is_frozen_mac = False
if sys.platform == "darwin":
    if getattr(sys, "frozen", False):
        is_frozen_mac = True


def get_path(relative_path):

    if not is_frozen_mac:
        return relative_path

    # Because Mac OS is actually terrible and needs special treatment 
    else:
        return os.path.join(pathlib.Path(os.path.abspath(sys.argv[0])).parent, relative_path)