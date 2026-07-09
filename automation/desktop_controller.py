"""
desktop_controller.py
---------------------
Smart desktop application launcher and window manager.

- If the app is already running → brings it to front (no re-launch).
- Wait for app to start: psutil polling (state-based, not fixed sleep).
- Covers 20+ common apps; falls back to os.startfile for unknowns.
"""
from __future__ import annotations

import os
import subprocess
import time

import psutil

from automation.window_manager import bring_to_front, wait_for_window


# ---------------------------------------------------------------------------
# App registry
# ---------------------------------------------------------------------------
# Each entry:
#   "launch"  : shell command to start the app (None = try by name)
#   "process" : process name as seen by psutil
#   "window"  : substring expected in the window title once open
#   "kill"    : process name(s) to kill on close

_APP_MAP: dict[str, dict] = {
    # Music / Media
    "spotify": {
        "launch": 'start "" "spotify:"',
        "process": "Spotify.exe",
        "window": "Spotify",
        "kill": ["Spotify.exe"],
    },
    # Code editors
    "vscode": {
        "launch": "code",
        "process": "Code.exe",
        "window": "Visual Studio Code",
        "kill": ["Code.exe"],
    },
    "vs code": {
        "launch": "code",
        "process": "Code.exe",
        "window": "Visual Studio Code",
        "kill": ["Code.exe"],
    },
    "visual studio code": {
        "launch": "code",
        "process": "Code.exe",
        "window": "Visual Studio Code",
        "kill": ["Code.exe"],
    },
    # Browsers
    "chrome": {
        "launch": "start chrome",
        "process": "chrome.exe",
        "window": "Google Chrome",
        "kill": ["chrome.exe"],
    },
    "google chrome": {
        "launch": "start chrome",
        "process": "chrome.exe",
        "window": "Google Chrome",
        "kill": ["chrome.exe"],
    },
    "edge": {
        "launch": "start msedge",
        "process": "msedge.exe",
        "window": "Microsoft Edge",
        "kill": ["msedge.exe"],
    },
    "microsoft edge": {
        "launch": "start msedge",
        "process": "msedge.exe",
        "window": "Microsoft Edge",
        "kill": ["msedge.exe"],
    },
    # Productivity
    "notepad": {
        "launch": "notepad.exe",
        "process": "notepad.exe",
        "window": "Notepad",
        "kill": ["notepad.exe"],
    },
    "notebook": {
        "launch": "notepad.exe",
        "process": "notepad.exe",
        "window": "Notepad",
        "kill": ["notepad.exe"],
    },
    "calculator": {
        "launch": "calc.exe",
        "process": "CalculatorApp.exe",
        "window": "Calculator",
        "kill": ["CalculatorApp.exe"],
    },
    "calculator app": {
        "launch": "calc.exe",
        "process": "CalculatorApp.exe",
        "window": "Calculator",
        "kill": ["CalculatorApp.exe"],
    },
    "paint": {
        "launch": "mspaint.exe",
        "process": "mspaint.exe",
        "window": "Paint",
        "kill": ["mspaint.exe"],
    },
    "explorer": {
        "launch": "explorer.exe",
        "process": "explorer.exe",
        "window": "File Explorer",
        "kill": [],  # Don't kill explorer
    },
    "file explorer": {
        "launch": "explorer.exe",
        "process": "explorer.exe",
        "window": "File Explorer",
        "kill": [],
    },
    # Communication
    "discord": {
        "launch": None,  # Try PATH / startfile
        "process": "Discord.exe",
        "window": "Discord",
        "kill": ["Discord.exe"],
    },
    "telegram": {
        "launch": None,
        "process": "Telegram.exe",
        "window": "Telegram",
        "kill": ["Telegram.exe"],
    },
    "whatsapp": {
        "launch": 'start "" "whatsapp:"',
        "process": "WhatsApp.exe",
        "window": "WhatsApp",
        "kill": ["WhatsApp.exe"],
    },
    # Gaming / Streaming
    "steam": {
        "launch": "start steam",
        "process": "steam.exe",
        "window": "Steam",
        "kill": ["steam.exe"],
    },
    "obs": {
        "launch": None,
        "process": "obs64.exe",
        "window": "OBS",
        "kill": ["obs64.exe"],
    },
    # System
    "task manager": {
        "launch": "taskmgr.exe",
        "process": "Taskmgr.exe",
        "window": "Task Manager",
        "kill": ["Taskmgr.exe"],
    },
    "control panel": {
        "launch": "control.exe",
        "process": "control.exe",
        "window": "Control Panel",
        "kill": [],
    },
    # Folders (open Windows Explorer at path)
    "downloads": {
        "launch": f'explorer "{os.path.join(os.path.expanduser("~"), "Downloads")}"',
        "process": "explorer.exe",
        "window": "Downloads",
        "kill": [],
    },
    "documents": {
        "launch": f'explorer "{os.path.join(os.path.expanduser("~"), "Documents")}"',
        "process": "explorer.exe",
        "window": "Documents",
        "kill": [],
    },
    "desktop": {
        "launch": f'explorer "{os.path.join(os.path.expanduser("~"), "Desktop")}"',
        "process": "explorer.exe",
        "window": "Desktop",
        "kill": [],
    },
    "pictures": {
        "launch": f'explorer "{os.path.join(os.path.expanduser("~"), "Pictures")}"',
        "process": "explorer.exe",
        "window": "Pictures",
        "kill": [],
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_running(process_name: str) -> bool:
    """Check if a process is running via psutil (no sleep)."""
    name_lower = process_name.lower()
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == name_lower:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def _kill_process(process_name: str) -> bool:
    killed = False
    name_lower = process_name.lower()
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == name_lower:
                proc.kill()
                killed = True
        except Exception:
            pass
    return killed


def _launch(app: dict) -> None:
    """Fire the launch command for an app entry."""
    cmd = app.get("launch")
    if cmd:
        os.system(cmd)
    else:
        # Try to start by process name (hope it's in PATH)
        proc_name = app.get("process", "")
        try:
            subprocess.Popen(proc_name)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def open_app(name: str) -> str:
    """
    Open a desktop application by name.
    - If already running → bring to front.
    - If not running → launch it.
    Returns a status string.
    """
    key = name.lower().strip()
    app = _APP_MAP.get(key)

    if app is None:
        # Unknown app — try os.startfile as last resort
        try:
            os.startfile(key)
            return f"✅ Launched {name}"
        except Exception:
            return f"❌ Application '{name}' not found. Make sure it is installed."

    process_name = app["process"]
    window_title = app["window"]

    if _is_running(process_name):
        bring_to_front(window_title)
        return f"✅ {name.title()} is already running — brought to front"

    _launch(app)
    return f"✅ Opening {name.title()}..."


def wait_for_app(name: str, timeout: float = 10.0) -> bool:
    """
    Wait until the app's process appears AND its window is visible.
    State-based: polls psutil + pygetwindow every 400 ms.
    Returns True if app is ready within `timeout` seconds.
    """
    key = name.lower().strip()
    app = _APP_MAP.get(key, {})
    process_name = app.get("process", name)
    window_title  = app.get("window", name)

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _is_running(process_name):
            # Process found — now wait for the window to appear
            remaining = deadline - time.monotonic()
            if remaining > 0 and wait_for_window(window_title, timeout=min(remaining, 5.0)):
                return True
            break
        time.sleep(0.4)  # Polling interval — not a fixed wait
    return False


def close_app(name: str) -> str:
    """Kill an application by name. Returns a status string."""
    key = name.lower().strip()
    app = _APP_MAP.get(key)
    kill_targets = app.get("kill", []) if app else [name]

    if not kill_targets:
        return f"⚠️ {name.title()} cannot be force-closed this way."

    killed_any = False
    for proc in kill_targets:
        if _kill_process(proc):
            killed_any = True

    return f"✅ Closed {name.title()}" if killed_any else f"⚠️ {name.title()} is not running"


def open_file_in_folder(folder: str, filename: str) -> str:
    """
    Search for `filename` inside the user folder `folder` and open it.
    Returns status string.
    """
    folder_paths = {
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "desktop":   os.path.join(os.path.expanduser("~"), "Desktop"),
        "pictures":  os.path.join(os.path.expanduser("~"), "Pictures"),
    }
    base = folder_paths.get(folder.lower(), folder)

    for root, _, files in os.walk(base):
        for f in files:
            if f.lower() == filename.lower():
                full_path = os.path.join(root, f)
                try:
                    os.startfile(full_path)
                    return f"📂 Opened {f}"
                except Exception as e:
                    return f"❌ Could not open {f}: {e}"

    return f"❌ File '{filename}' not found in {folder.title()}"


# Expose the app registry for use by intent_parser
NATIVE_APP_NAMES: frozenset[str] = frozenset(_APP_MAP.keys())
