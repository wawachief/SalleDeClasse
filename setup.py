# Author: Olivier Lécluse
# License GPL-3

#
# Digirule CPU Core
#

import sys
from cx_Freeze import setup, Executable
from configparser import ConfigParser

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "pyside2", "sqlite3", "pyqrcode", "engineio", 'socketio', "eventlet", 'flask_socketio', "configparser", "jinja2.ext", "dns", "csv"],
    "include_files": ["doc/", "assets/", "src/", "README.md", "config.ini"],
    "excludes": ["tkinter", "tk"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    if 'bdist_msi' in sys.argv:
        sys.argv += ['--initial-target-dir', 'c:\sdc']

config = ConfigParser()
config.read("config.ini")

setup(  name = "SalleDeClasse",
        version = config.get('main', 'version'),
        description = "Salle de Classe",
        author="Olivier Lecluse - Thomas Lecluse - Nicolas Lecluse",
        options = {"build_exe": build_exe_options},
        executables = [Executable("sdc.py", base=base, icon="C:\sdc.ico")])