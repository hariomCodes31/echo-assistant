"""
scheduler.py
------------
Schedule a command to run at a specific wall-clock time (HH:MM, 12- or 24-hour).

Usage (internal):
    from automation.scheduler import schedule_command
    schedule_command("3:10pm", "play despacito")

The command is executed by re-routing through modules.router.execute / execute_multiple
so it benefits from the full pipeline (planner → router → AI fallback).

Thread-safety: uses a daemon threading.Timer so it is automatically cleaned
up when the main process exits.
"""
from __future__ import annotations

import re
import threading
from datetime import datetime, timedelta
from typing import Callable

# Registry of pending timers: label → Timer
_pending: dict[str, threading.Timer] = {}


def _seconds_until(hour: int, minute: int) -> float:
    """Return seconds until the next occurrence of HH:MM (today or tomorrow)."""
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        # Already passed today → schedule for tomorrow
        target += timedelta(days=1)
    return (target - now).total_seconds()


def _parse_time(time_str: str) -> tuple[int, int] | None:
    """
    Parse a time string such as '3:10pm', '15:10', '5:01am', '3:10 PM'.
    Returns (hour_24, minute) or None if unparseable.
    """
    time_str = time_str.strip().lower().replace(" ", "")

    # 12-hour with am/pm
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(am|pm)", time_str)
    if m:
        h, mn, meridiem = int(m.group(1)), int(m.group(2)), m.group(3)
        if meridiem == "am":
            h = 0 if h == 12 else h
        else:
            h = 12 if h == 12 else h + 12
        if 0 <= h <= 23 and 0 <= mn <= 59:
            return h, mn
        return None

    # 24-hour  e.g. 15:10
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", time_str)
    if m:
        h, mn = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mn <= 59:
            return h, mn
        return None

    return None


def schedule_command(
    time_str: str,
    command: str,
    on_fire: Callable[[str, str], None] | None = None,
) -> str:
    """
    Schedule `command` to execute at `time_str`.

    Parameters
    ----------
    time_str : str   — Time string, e.g. "3:10pm" or "15:10".
    command  : str   — The command to run (passed to the router pipeline).
    on_fire  : callable(time_str, command) — Optional callback invoked when
                the timer fires (used to send TTS / chat feedback).

    Returns
    -------
    str — Human-readable confirmation message.
    """
    parsed = _parse_time(time_str)
    if parsed is None:
        return f"❌ Could not parse time '{time_str}'. Use format like '3:10pm' or '15:10'."

    hour, minute = parsed
    delay = _seconds_until(hour, minute)

    label = f"{time_str}::{command}"

    # Cancel any existing timer for the same slot
    if label in _pending:
        _pending[label].cancel()

    def _fire():
        _pending.pop(label, None)
        # Execute through the router pipeline
        try:
            from modules.router import execute_multiple, execute
            from ai import ask_ai

            responses = execute_multiple(command)
            if responses:
                result = "\n".join(responses)
            else:
                result = execute(command)
                if result is None:
                    result = ask_ai(command)
        except Exception as e:
            result = f"❌ Scheduled command failed: {e}"

        if on_fire:
            try:
                on_fire(time_str, command)
            except Exception:
                pass

        # TTS feedback
        try:
            from modules.voice_manager import voice_manager
            voice_manager.tts_player.speak(f"Scheduled command: {command}")
        except Exception:
            pass

    timer = threading.Timer(delay, _fire)
    timer.daemon = True
    timer.start()
    _pending[label] = timer

    # Friendly confirmation
    target_dt = datetime.now().replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    # If already past today, show tomorrow
    if target_dt <= datetime.now():
        from datetime import timedelta
        target_dt += timedelta(days=1)

    friendly = target_dt.strftime("%I:%M %p").lstrip("0")
    mins_away = int(delay / 60)
    if mins_away < 60:
        eta = f"{mins_away} min{'s' if mins_away != 1 else ''}"
    else:
        hours_away = mins_away // 60
        rem_mins = mins_away % 60
        eta = f"{hours_away}h {rem_mins}m" if rem_mins else f"{hours_away}h"

    return (
        f"⏰ Scheduled: **{command}** at **{friendly}** "
        f"(in ~{eta})"
    )


def cancel_all() -> str:
    """Cancel all pending scheduled commands."""
    count = len(_pending)
    for t in _pending.values():
        t.cancel()
    _pending.clear()
    return f"✅ Cancelled {count} scheduled command{'s' if count != 1 else ''}."


def list_scheduled() -> str:
    """Return a human-readable list of all pending scheduled commands."""
    if not _pending:
        return "📭 No commands currently scheduled."
    lines = ["⏰ **Pending Scheduled Commands:**"]
    for label in _pending:
        time_part, cmd_part = label.split("::", 1)
        lines.append(f"  • `{cmd_part}` at **{time_part}**")
    return "\n".join(lines)
