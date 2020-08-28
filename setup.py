# Salle de classe by Lecluse DevCorp
# file author : Thomas Lecluse
# Licence GPL-v3 - see LICENCE.txt

import sys
from cx_Freeze import setup, Executable
from configparser import ConfigParser

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "pyside2", "sqlite3", "pyqrcode", "engineio", 'socketio', "eventlet", 'flask_socketio', "configparser", "jinja2.ext", "dns", "csv"],
    "include_files": ["doc/", "assets/", "src/", "README.md", "config.ini"],
    "excludes": ["tkinter", "tk"]
}
bdist_msi_options = {
    "upgrade_code": "{96a85bac-52af-4019-9e94-3afcc9e1ad0c}"
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
        options = {"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
        executables = [Executable("sdc.py", base=base, icon="C:\sdc.ico")])