import importlib.util
import subprocess
import sys
if importlib.util.find_spec("pyautogui") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
import pyautogui
for i in range(50):
    pyautogui.hotkey("ctrl","v")
    pyautogui.hotkey("enter")
    pyautogui.hotkey("enter")