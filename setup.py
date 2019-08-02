from cx_Freeze import setup, Executable
import os.path
import sys

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable("Main.py", base=base)]

packages = ["idna", "pygame", "math", "random", "networkx", "colorsys", "time", "Node", "graphSetup", "numpy"]
options = {
    'build_exe': {
        'packages':packages,
    },
}

setup(
    name = "GD",
    options = options,
    version = "0.0.1",
    description = 'AcademyNEXT',
    executables = executables
)
