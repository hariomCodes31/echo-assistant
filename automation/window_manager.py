"""
window_manager.py
-----------------
Windows foreground window utilities.
Uses pygetwindow for title-based lookup and ctypes as fallback.
No fixed sleeps — all waits are psutil/window-state based.
"""
import time
import ctypes
import ctypes.wintypes

try:
    import pygetwindow as gw
    _HAS_GW = True
except ImportError:
    _HAS_GW = False


def bring_to_front(window_title: str) -> bool:
    """
    Bring the first window whose title contains `window_title` to the foreground.
    Returns True if successful.
    """
    if _HAS_GW:
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            win = windows[0]
            try:
                if win.isMinimized:
                    win.restore()
                win.activate()
                return True
            except Exception:
                pass

    # ctypes fallback — enumerate all windows and match title substring
    return _ctypes_bring_to_front(window_title)


def _ctypes_bring_to_front(title_substring: str) -> bool:
    """Find and foreground a window by partial title match via EnumWindows."""
    found_hwnd = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
    def _enum_callback(hwnd, lParam):
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
        if title_substring.lower() in buf.value.lower():
            if ctypes.windll.user32.IsWindowVisible(hwnd):
                found_hwnd.append(hwnd)
                return False  # Stop enumeration
        return True

    ctypes.windll.user32.EnumWindows(_enum_callback, 0)
    if found_hwnd:
        hwnd = found_hwnd[0]
        # Restore if minimised
        SW_RESTORE = 9
        ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        return True
    return False


def wait_for_window(window_title: str, timeout: float = 8.0) -> bool:
    """
    Poll until a window whose title contains `window_title` appears.
    State-based: checks window existence every 400 ms, no fixed sleep duration.
    Returns True if window found within timeout.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if _HAS_GW:
            if gw.getWindowsWithTitle(window_title):
                return True
        else:
            # ctypes check
            found = []

            @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            def _cb(hwnd, lp):
                buf = ctypes.create_unicode_buffer(256)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
                if window_title.lower() in buf.value.lower():
                    found.append(hwnd)
                    return False
                return True

            ctypes.windll.user32.EnumWindows(_cb, 0)
            if found:
                return True

        time.sleep(0.4)  # Polling interval — not a fixed duration wait
    return False


def is_window_open(window_title: str) -> bool:
    """Return True if any visible window contains `window_title`."""
    if _HAS_GW:
        return bool(gw.getWindowsWithTitle(window_title))
    return wait_for_window(window_title, timeout=0.0)
