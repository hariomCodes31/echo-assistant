import os
import subprocess
import webbrowser
from datetime import datetime
import ctypes

import pyautogui
import keyboard
import psutil

SCREENSHOT_FOLDER = "screenshots"
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


def _kill(process_name):
    killed = False

    for process in psutil.process_iter(["name"]):
        try:
            if (
                process.info["name"]
                and process.info["name"].lower() == process_name.lower()
            ):
                process.kill()
                killed = True
        except Exception:
            pass

    return killed


def open_spotify():
    """
    Opens Spotify using the protocol first.
    Falls back to WindowsApps executable if needed.
    """

    try:
        os.system('start "" "spotify:"')
        return "✅ Opening Spotify..."
    except Exception:
        pass

    try:
        spotify_path = os.path.join(
            os.environ["LOCALAPPDATA"],
            "Microsoft",
            "WindowsApps",
            "Spotify.exe",
        )

        subprocess.Popen(spotify_path)
        return "✅ Opening Spotify..."
    except Exception:
        return "❌ Spotify is not installed."


def desktop(command):

    cmd = command.lower().strip()

    # ---------------- OPEN APPS ---------------- #

    apps = {

        "open chrome":
            lambda: (
                webbrowser.open("https://google.com"),
                "✅ Opening Chrome..."
            )[1],

        "open vscode":
            lambda: (
                os.system("code"),
                "✅ Opening VS Code..."
            )[1],

        "open vs code":
            lambda: (
                os.system("code"),
                "✅ Opening VS Code..."
            )[1],

        "open calculator":
            lambda: (
                subprocess.Popen("calc.exe"),
                "✅ Opening Calculator..."
            )[1],

        "open notepad":
            lambda: (
                subprocess.Popen("notepad.exe"),
                "✅ Opening Notepad..."
            )[1],

        "open paint":
            lambda: (
                subprocess.Popen("mspaint.exe"),
                "✅ Opening Paint..."
            )[1],

        "open explorer":
            lambda: (
                subprocess.Popen("explorer.exe"),
                "✅ Opening Explorer..."
            )[1],

        "open file explorer":
            lambda: (
                subprocess.Popen("explorer.exe"),
                "✅ Opening Explorer..."
            )[1],

        "open spotify":
            open_spotify,

    }

    if cmd in apps:
        return apps[cmd]()

    # ---------------- OPEN FOLDERS ---------------- #

    folders = {

        "open downloads": "Downloads",
        "open documents": "Documents",
        "open desktop": "Desktop",
        "open pictures": "Pictures",

    }

    if cmd in folders:

        path = os.path.join(
            os.path.expanduser("~"),
            folders[cmd]
        )

        os.startfile(path)

        return f"📂 Opening {folders[cmd]}"

    # ---------------- CLOSE APPS ---------------- #

    closes = {

        "close chrome": "chrome.exe",
        "close vscode": "Code.exe",
        "close vs code": "Code.exe",
        "close calculator": "CalculatorApp.exe",
        "close notepad": "notepad.exe",
        "close paint": "mspaint.exe",
        "close explorer": "explorer.exe",

    }

    if cmd in closes:

        if _kill(closes[cmd]):
            return "✅ Closed"

        return "⚠️ App not running"

    # ---------------- TYPE ---------------- #

    if cmd.startswith("type "):

        text = command[5:]

        pyautogui.write(
            text,
            interval=0.02
        )

        return "⌨️ Typed."

    # ---------------- HOTKEYS ---------------- #

        # ---------------- HOTKEYS ---------------- #

    hotkeys = {

        "press enter": ["enter"],
        "press tab": ["tab"],
        "press escape": ["esc"],
        "press backspace": ["backspace"],
        "press delete": ["delete"],
        "press space": ["space"],

        "copy": ["ctrl", "c"],
        "paste": ["ctrl", "v"],
        "cut": ["ctrl", "x"],
        "undo": ["ctrl", "z"],
        "redo": ["ctrl", "y"],
        "select all": ["ctrl", "a"],

        "alt tab": ["alt", "tab"],
        "switch window": ["alt", "tab"],
        "show desktop": ["win", "d"],

    }

    if cmd in hotkeys:

        keyboard.press_and_release(
            "+".join(hotkeys[cmd])
        )

        return f"⌨️ {cmd.title()}"

    # ---------------- MOUSE ---------------- #

    if cmd == "click":

        pyautogui.click()

        return "🖱️ Clicked"

    if cmd == "double click":

        pyautogui.doubleClick()

        return "🖱️ Double Clicked"

    if cmd == "right click":

        pyautogui.rightClick()

        return "🖱️ Right Clicked"

    if cmd == "scroll up":

        pyautogui.scroll(600)

        return "🖱️ Scrolled Up"

    if cmd == "scroll down":

        pyautogui.scroll(-600)

        return "🖱️ Scrolled Down"

    

    
    # ---------------- SYSTEM ---------------- #

    if cmd == "lock pc":

        ctypes.windll.user32.LockWorkStation()

        return "🔒 Locking PC"

    if cmd == "restart":

        os.system("shutdown /r /t 0")

        return "🔄 Restarting"

    if cmd == "shutdown":

        os.system("shutdown /s /t 0")

        return "⛔ Shutting down"

    if cmd == "sleep":

        os.system(
            "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
        )

        return "💤 Sleeping"

    # ---------------- SCREENSHOT ---------------- #

    if cmd == "take screenshot":

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H-%M-%S"
        )

        filename = f"screenshot_{timestamp}.png"

        filepath = os.path.join(
            SCREENSHOT_FOLDER,
            filename
        )

        image = pyautogui.screenshot()

        image.save(filepath)

        return f"📸 Screenshot saved:\n{filepath}"

    return None