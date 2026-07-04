"""
search_actions.py
-----------------
Native app search/play sequences that can't be done via browser.

Spotify: uses the native Windows app via keyboard shortcuts.
  - Ctrl+L  → focus the search bar (Spotify 1.x)
  - Ctrl+K  → opens the search/command bar (newer builds)
  The minimal time.sleep() calls here are genuinely required because:
    we send a keyboard shortcut to a native Win32 window and must wait
    for the UI to react — there is no queryable state to poll instead.
    These are kept as short as possible (≤ 0.3 s each).

YouTube search: uses browser_actions (state-based waits via Playwright).
"""
from __future__ import annotations

import time

import keyboard

from automation import browser_actions, desktop_controller
from automation.window_manager import bring_to_front, wait_for_window


# ---------------------------------------------------------------------------
# Spotify (native app)
# ---------------------------------------------------------------------------

def spotify_play(query: str) -> str:
    """
    Open Spotify, focus it, use keyboard shortcut to search, and play.
    Returns a status string.
    """
    # 1. Ensure Spotify is open
    status = desktop_controller.open_app("spotify")
    desktop_controller.wait_for_app("spotify", timeout=12.0)

    # 2. Bring Spotify window to front
    if not bring_to_front("Spotify"):
        return f"⚠️ Could not focus Spotify. {status}"

    # 3. Open Spotify search — try Ctrl+K first (newer), then Ctrl+L (legacy)
    #    Minimal sleep after shortcut: required for Win32 UI to render the search box
    keyboard.press_and_release("ctrl+k")
    time.sleep(0.25)  # UI render wait — no queryable state available

    # 4. Clear any existing text and type the query
    keyboard.press_and_release("ctrl+a")
    keyboard.write(query, delay=0.04)  # Inter-key delay for reliability
    time.sleep(0.1)
    keyboard.press_and_release("enter")

    # 5. Brief pause then press Enter again to start first result
    time.sleep(0.5)  # Wait for Spotify to show results — no queryable state
    keyboard.press_and_release("enter")

    return f"🎵 Playing '{query}' on Spotify"


# ---------------------------------------------------------------------------
# YouTube (browser)
# ---------------------------------------------------------------------------

def youtube_search(query: str) -> str:
    """
    Open YouTube in the Playwright browser and search for `query`.
    Uses state-based waits via browser_actions.
    """
    page = browser_actions.open_site("youtube")
    success = browser_actions.search_on_site(page, query)
    if success:
        return f"▶️ Searching YouTube for '{query}'"
    return f"⚠️ Opened YouTube but could not locate the search box"


def youtube_play(query: str) -> str:
    """
    Open YouTube, search, and click the first video result.
    Uses state-based waits via Playwright.
    """
    page = browser_actions.open_site("youtube")
    browser_actions.search_on_site(page, query)

    # Click the first video result — wait for it to appear (state-based)
    video_selectors = [
        "ytd-video-renderer #video-title",
        "a#video-title",
        "ytd-compact-video-renderer a",
    ]
    for sel in video_selectors:
        if browser_actions.click_element(page, sel, timeout_ms=5_000):
            return f"▶️ Playing '{query}' on YouTube"

    return f"▶️ Searched YouTube for '{query}' — click a result to play"
