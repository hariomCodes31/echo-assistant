"""
executor.py
-----------
Receives a parsed step list from intent_parser and executes each action
in sequence, yielding a status string after every step.

State tracking:
  - last_opened_site  : remembered across steps so a bare "browser_search"
                        step knows which page to search on.
  - last_page         : the live Playwright Page object from the previous step.

No fixed sleep() calls — all waits are delegated to the controllers/actions
which use Playwright state-based waits and psutil polling.
"""
from __future__ import annotations

from typing import Generator

from automation import browser_actions, browser_controller, desktop_controller, search_actions


# ---------------------------------------------------------------------------
# Internal dispatcher
# ---------------------------------------------------------------------------

def _dispatch(
    step: dict,
    state: dict,
) -> str:
    """
    Execute one action step, mutate `state` as needed, return a status string.
    `state` holds: last_opened_site (str|None), last_page (Page|None).
    """
    action = step.get("action", "")

    # ── Open a website ──────────────────────────────────────────────────────
    if action == "open_website":
        target = step["target"]
        try:
            page = browser_actions.open_site(target)
            state["last_page"] = page
            state["last_opened_site"] = target
            url = browser_actions.resolve_url(target)
            return f"🌐 Opened {target.title()} ({url})"
        except Exception as e:
            return f"❌ Could not open {target}: {e}"

    # ── Open a desktop application ───────────────────────────────────────────
    elif action == "open_app":
        target = step["target"]
        result = desktop_controller.open_app(target)
        # Wait for the app to be ready (state-based psutil polling)
        desktop_controller.wait_for_app(target, timeout=10.0)
        state["last_opened_site"] = None   # Now in desktop context
        state["last_page"] = None
        return result

    # ── Open a folder ────────────────────────────────────────────────────────
    elif action == "open_folder":
        target = step["target"]
        result = desktop_controller.open_app(target)  # Folder entries are in _APP_MAP
        desktop_controller.wait_for_app("explorer", timeout=6.0)
        return result

    # ── Search inside the currently open browser page ─────────────────────
    elif action == "browser_search":
        query  = step.get("query", "")
        target = step.get("target") or state.get("last_opened_site")
        page   = state.get("last_page")

        if page is None:
            # No page open yet — open the target site first
            if target:
                try:
                    page = browser_actions.open_site(target)
                    state["last_page"] = page
                    state["last_opened_site"] = target
                except Exception as e:
                    return f"❌ Could not open {target} to search: {e}"
            else:
                # No target — fall back to Google Search
                from tools.browser import search_google
                search_google(query)
                return f"🔍 Searched Google for '{query}'"

        success = browser_actions.search_on_site(page, query)
        site_label = (target or "the site").title()
        if success:
            return f"🔍 Searched {site_label} for '{query}'"
        return f"⚠️ Opened {site_label} but couldn't locate a search box"

    # ── Play music on Spotify (native app) ───────────────────────────────────
    elif action == "play_music":
        query = step.get("query", "")
        return search_actions.spotify_play(query)

    # ── Search and play on YouTube ────────────────────────────────────────────
    elif action == "youtube_play":
        query = step.get("query", "")
        result = search_actions.youtube_play(query)
        # Update page state
        page = browser_controller.current_page()
        if page:
            state["last_page"] = page
            state["last_opened_site"] = "youtube"
        return result

    # ── Close an application ─────────────────────────────────────────────────
    elif action == "close_app":
        target = step.get("target", "")
        return desktop_controller.close_app(target)

    # ── Open a specific file inside a folder ─────────────────────────────────
    elif action == "open_file":
        folder   = step.get("folder", "")
        filename = step.get("filename", "")
        return desktop_controller.open_file_in_folder(folder, filename)

    # ── Schedule a command to run at a future time ───────────────────────────
    elif action == "scheduled_command":
        time_str = step.get("time", "")
        command  = step.get("command", "")
        from automation.scheduler import schedule_command
        return schedule_command(time_str, command)

    # ── Type text into the currently focused window ───────────────────────────
    elif action == "type_text":
        text = step.get("text", "")
        if not text:
            return "⚠️ No text provided to type."
        try:
            import time as _time
            import pyautogui
            _time.sleep(0.6)   # Give the newly-opened app time to focus
            pyautogui.write(text, interval=0.03)
            return f"⌨️ Typed: {text}"
        except Exception as e:
            return f"❌ Could not type text: {e}"

    # ── Open Calculator and evaluate an expression ────────────────────────────
    elif action == "calculate":
        expression = step.get("expression", "")
        if not expression:
            return "⚠️ No expression provided to calculate."
        try:
            import time as _time
            import pyautogui

            # Open calculator (reuse desktop_controller so it handles already-running)
            open_result = desktop_controller.open_app("calculator")
            desktop_controller.wait_for_app("calculator", timeout=8.0)
            _time.sleep(0.8)   # Let the Calculator window fully render and focus

            # Clear any previous value
            pyautogui.press('escape')
            for ch in expression:
                if ch.isdigit():
                    pyautogui.press(ch)
                elif ch == '+':
                    pyautogui.press('+')
                elif ch == '-':
                    pyautogui.press('-')
                elif ch == '*':
                    pyautogui.press('*')
                elif ch == '/':
                    pyautogui.press('/')
                elif ch == '(':
                    pyautogui.hotkey('shift', '9')
                elif ch == ')':
                    pyautogui.hotkey('shift', '0')
                elif ch == '.':
                    pyautogui.press('.')
                elif ch == ' ':
                    pass   # skip spaces
            pyautogui.press('enter')   # press = to evaluate

            return f"🧮 {open_result} — Calculated: **{expression}**"
        except Exception as e:
            return f"❌ Calculator failed: {e}"

    # ── Google web search (fallback) ─────────────────────────────────────────
    elif action == "web_search":
        query = step.get("query", "")
        from tools.browser import search_google
        search_google(query)
        return f"🔍 Searched Google for '{query}'"

    return f"⚠️ Unknown action: {action}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute_plan(steps: list[dict]) -> Generator[str, None, None]:
    """
    Execute a list of action steps in order.
    Yields a human-readable status string after each step.
    Yields a final completion line when all steps are done.
    Never raises — errors are caught and yielded as status strings.
    """
    state: dict = {
        "last_opened_site": None,
        "last_page": None,
    }

    total = len(steps)
    for i, step in enumerate(steps, start=1):
        action = step.get("action", "?")
        try:
            status = _dispatch(step, state)
        except Exception as e:
            status = f"❌ Step {i} ({action}) failed: {e}"

        yield f"[{i}/{total}] {status}"

    yield "✅ All steps completed"
