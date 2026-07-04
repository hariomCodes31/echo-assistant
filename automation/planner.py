"""
planner.py
----------
The single public entry point for the automation engine.
Called by modules/router.py before any existing routing logic.

run(command) → str | None
  • Returns a formatted result string when the automation engine handles it.
  • Returns None when the existing router should handle it instead.

Voice feedback is sent through voice_manager.tts_player.speak()
for each step so the user hears progress while the UI updates.
"""
from __future__ import annotations

from automation import executor, intent_parser


def run(command: str) -> str | None:
    """
    Parse `command` into a task plan and execute it.

    Returns:
        str   — assembled execution log to display in chat.
        None  — planner cannot handle this; let the existing router proceed.
    """
    # Parse — returns None if the existing router owns this command
    steps = intent_parser.parse(command)
    if not steps:
        return None

    # Build a progress log by collecting all yielded status lines
    lines: list[str] = [
        f"**🤖 ECHO X Automation — {len(steps)}-step plan**",
    ]

    # Speak the first step as immediate voice feedback
    _speak_async(f"Starting execution. {len(steps)} step{'s' if len(steps) > 1 else ''}.")

    for status_line in executor.execute_plan(steps):
        lines.append(status_line)
        # Speak each status update in the background (non-blocking)
        _speak_async(_tts_text(status_line))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Voice feedback helpers
# ---------------------------------------------------------------------------

def _speak_async(text: str) -> None:
    """Speak text through the existing TTS player without blocking execution."""
    try:
        from modules.voice_manager import voice_manager
        voice_manager.tts_player.speak(text)
    except Exception:
        pass  # Voice is optional — never block execution on TTS failure


def _tts_text(line: str) -> str:
    """
    Strip emoji and status brackets from a log line for cleaner TTS output.
    e.g. "[2/3] 🌐 Opened Instagram" → "Opened Instagram"
    """
    import re
    # Remove [n/m] prefix
    line = re.sub(r"^\[\d+/\d+\]\s*", "", line)
    # Remove common emoji
    for ch in ["🌐", "🔍", "✅", "❌", "⚠️", "🎵", "▶️", "📂", "🖥️", "🤖", "**"]:
        line = line.replace(ch, "")
    return line.strip()
