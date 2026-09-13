import importlib.util
import subprocess
import sys
import os
import warnings
if importlib.util.find_spec('pygetwindow') is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygetwindow"])
import pygetwindow
banned=['family']
openedWindows=pygetwindow.getAllTitles()
while True:
    if openedWindows!=pygetwindow.getAllTitles():
        openedWindows=pygetwindow.getAllTitles()
        os.system('cls')
        print(f"All Opened Windows: {openedWindows} \nCurrently active window: {pygetwindow.getActiveWindowTitle()} ")
    for ban in banned:
        for window in openedWindows:
            if ban.lower() in window.lower():
                try:
                    toBan=pygetwindow.getWindowsWithTitle(window)[0]
                except:
                    continue
                try:
                    toBan.close()
                    warnings.warn(f"Closed {window}!")
                except:
                    try:
                        toBan.minimize()
                        warnings.warn(f"Minimized {window}!")
                    except:
                        try:
                            toBan.hide()
                            warnings.warn(f"Hid {window}!")
                        except:
                            warnings.warn(f"Close {window} right now!")