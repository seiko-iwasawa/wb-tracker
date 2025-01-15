import pathlib
import shutil
import sys

_home = pathlib.Path.home()
"""Home path."""
if sys.platform == "win32":
    appdata = _home / "AppData/Roaming"
elif sys.platform == "linux":
    appdata = _home / ".local/share"
elif sys.platform == "darwin":
    appdata = _home / "Library/Application Support"
else:
    appdata = _home
root = appdata / "WB Tracker"
debug_root = pathlib.Path(".")

DEBUG = False

if DEBUG:
    root = debug_root
else:
    if (
        not root.exists()
        or open(debug_root / "data" / "version.txt").readline()
        != open(root / "data" / "version.txt").readline()
    ):
        if root.exists():
            shutil.rmtree(root)
        root.mkdir()
        shutil.copytree(debug_root / "data", root / "data")
