import sys
from pathlib import Path


def update_path():
    here = Path(__file__)
    to_append = str(here.resolve().parent.parent)
    print(to_append)
    sys.path.append(to_append)
    return to_append
