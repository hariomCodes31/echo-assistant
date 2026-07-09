"""
intent_parser.py
----------------
Hybrid command parser:
  Fast path  — regex/keyword matching, zero latency, zero API cost.
  Slow path  — Groq LLM for genuinely ambiguous or novel compound commands.

POLICY:
  • Single-step simple commands (open notepad, take screenshot, weather in X)
    → return None so the existing router handles them unchanged.
  • Multi-step compound commands OR commands requiring browser automation
    → parse into a list of action dicts and return them.

Action dict schema:
  {"action": "open_website",       "target": "<name_or_url>"}
  {"action": "open_app",           "target": "<app_name>"}
  {"action": "open_folder",        "target": "<folder_name>"}
  {"action": "browser_search",     "target": "<site>", "query": "<query>"}
  {"action": "play_music",         "query": "<song_name>"}
  {"action": "youtube_play",       "query": "<song_or_video>"}
  {"action": "close_app",          "target": "<app_name>"}
  {"action": "open_file",          "folder": "<folder>", "filename": "<file>"}
  {"action": "web_search",         "query": "<query>"}
  {"action": "scheduled_command",  "time": "<HH:MMam/pm>", "command": "<command>"}
  {"action": "type_text",          "text": "<text_to_type>"}
  {"action": "calculate",          "expression": "<math_expression>"}
"""
from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------------------------------------------------------------------------
# App / site categorisation (imported from controller to stay DRY)
# ---------------------------------------------------------------------------
from automation.desktop_controller import NATIVE_APP_NAMES

# Website-only names (never a native app)
_WEBSITE_NAMES: frozenset[str] = frozenset({
    "instagram", "facebook", "linkedin", "reddit", "twitter", "x",
    "youtube", "amazon", "flipkart", "netflix", "hotstar", "primevideo",
    "prime video", "chatgpt", "claude", "gemini", "whatsapp",
    "gmail", "drive", "google drive", "docs", "google docs",
    "sheets", "slides", "calendar", "photos", "meet",
    "stackoverflow", "medium", "notion", "figma", "canva",
    "github", "jiocinema", "jio", "classroom",
})

# Verbs that introduce a new sub-command in a compound command
_ACTION_VERB_RE = re.compile(
    r"\b(open|launch|go\s+to|navigate\s+to|search(?:\s+for)?|play|close|type|calculate)\b",
    re.IGNORECASE,
)

# Pattern: "<command> at <time>"  — scheduling suffix
_SCHEDULE_RE = re.compile(
    r"^(.+?)\s+at\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)\s*$",
    re.IGNORECASE,
)

# Separators that always introduce a new step
_HARD_SEP_RE = re.compile(
    r"\s+then\s+|\s*,\s*then\s+",
    re.IGNORECASE,
)

# "and" followed by an action verb → also a step separator
_SOFT_SEP_RE = re.compile(
    r"\s+and\s+(?=(?:open|launch|go\s+to|navigate\s+to|search|play|close|type|calculate)\b)",
    re.IGNORECASE,
)

# Commands the existing router already handles perfectly — return None
_ROUTER_OWNS = re.compile(
    r"^(take\s+screenshot|weather\s+in|scroll\s+(up|down)|click|"
    r"double\s+click|right\s+click|copy|paste|cut|undo|redo|"
    r"select\s+all|alt\s+tab|show\s+desktop|press\s+\w+|type\s+|"
    r"lock\s+pc|restart|shutdown|sleep|analyze|describe|read\s+text)",
    re.IGNORECASE,
)


# File extensions that should be opened as files, not websites
_FILE_EXTENSIONS = frozenset({
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".zip", ".rar", ".mp3", ".mp4", ".jpg",
    ".jpeg", ".png", ".gif", ".exe", ".msi",
})


def _is_file(name: str) -> bool:
    """True if name looks like a filename (has a known file extension)."""
    import os
    _, ext = os.path.splitext(name.lower())
    return ext in _FILE_EXTENSIONS


# ---------------------------------------------------------------------------
# Fast path helpers
# ---------------------------------------------------------------------------

def _is_native_app(name: str) -> bool:
    return name.lower().strip() in NATIVE_APP_NAMES


def _is_website(name: str) -> bool:
    return name.lower().strip() in _WEBSITE_NAMES


def _make_open_step(target: str, context_folder: str | None = None) -> dict:
    """Create the right open step based on whether target is an app, file, or site."""
    t = target.lower().strip()
    if _is_file(t):
        return {"action": "open_file", "folder": context_folder, "filename": t}
    if t in ("downloads", "documents", "desktop", "pictures"):
        return {"action": "open_folder", "target": t}
    if _is_native_app(t):
        return {"action": "open_app", "target": t}
    return {"action": "open_website", "target": t}


def _split_compound(command: str) -> list[str]:
    """
    Split a compound command into individual sub-command strings.
    Hard splits (then) always split; soft splits (and + verb) also split.
    """
    # Apply hard separators first
    parts = _HARD_SEP_RE.split(command)
    # Apply soft separators within each part
    result = []
    for part in parts:
        result.extend(_SOFT_SEP_RE.split(part))
    return [p.strip() for p in result if p.strip()]


def _parse_single(cmd: str, context_site: str | None = None) -> dict | list[dict] | None:
    """
    Parse a single-segment command into one or more action dicts.
    `context_site` is the most recently opened site (for bare 'search X' steps).
    Returns None if unrecognised.
    """
    cmd = cmd.strip()
    low = cmd.lower()

    # open/launch/go to X [and/then search Y]
    m = re.match(
        r"^(?:open|launch|go\s+to|navigate\s+to)\s+(.+?)(?:\s+(?:and\s+|then\s+)?search(?:\s+for)?\s+(.+))?$",
        cmd, re.IGNORECASE
    )
    if m:
        target = m.group(1).strip()
        query  = (m.group(2) or "").strip()
        steps = [_make_open_step(target)]
        if query:
            # Carry the target name into browser_search so executor knows the page
            steps.append({"action": "browser_search", "target": target.lower(), "query": query})
        return steps

    # open/launch X and play Y  (Spotify + song, or YouTube + video)
    m = re.match(
        r"^(?:open|launch)\s+(.+?)\s+(?:and\s+|then\s+)?play\s+(.+)$",
        cmd, re.IGNORECASE
    )
    if m:
        app   = m.group(1).strip().lower()
        query = m.group(2).strip()
        steps = [_make_open_step(app)]
        if app == "spotify":
            steps.append({"action": "play_music", "query": query})
        else:
            steps.append({"action": "youtube_play", "query": query})
        return steps

    # search [for] X  (standalone — uses context_site if available)
    m = re.match(r"^search(?:\s+for)?\s+(.+)$", cmd, re.IGNORECASE)
    if m:
        return {"action": "browser_search", "target": context_site, "query": m.group(1).strip()}

    # play X  (standalone — defaults to Spotify)
    m = re.match(r"^play\s+(.+)$", cmd, re.IGNORECASE)
    if m:
        return {"action": "play_music", "query": m.group(1).strip()}

    # close X
    m = re.match(r"^close\s+(.+)$", cmd, re.IGNORECASE)
    if m:
        return {"action": "close_app", "target": m.group(1).strip().lower()}

    # type <text>  — type text into focused window
    m = re.match(r"^type\s+(.+)$", cmd, re.IGNORECASE)
    if m:
        return {"action": "type_text", "text": m.group(1).strip()}

    # calculate <expression>  — open calculator and compute
    m = re.match(r"^calculate\s+(.+)$", cmd, re.IGNORECASE)
    if m:
        return {"action": "calculate", "expression": m.group(1).strip()}

    return None


def _is_compound(command: str) -> bool:
    """True if the command has more than one step."""
    parts = _split_compound(command)
    return len(parts) > 1


def _fast_parse(command: str) -> list[dict] | None:
    """
    Pure-Python fast path. Returns a step list or None.
    Single-step commands that router already owns → None.
    """
    # ── Scheduling: "<command> at HH:MMam/pm" ───────────────────────────────
    # Check BEFORE the router-owns guard so scheduled single commands are caught.
    m = _SCHEDULE_RE.match(command)
    if m:
        inner_cmd = m.group(1).strip()
        time_str  = m.group(2).strip()
        return [{"action": "scheduled_command", "time": time_str, "command": inner_cmd}]

    # Hand off to router if it owns this command type
    if _ROUTER_OWNS.match(command):
        return None

    parts = _split_compound(command)

    if len(parts) == 1:
        # Single command — only handle if it produces multiple sub-steps (e.g. open+search)
        step = _parse_single(command)
        if step is None:
            return None

        # Normalise to list
        steps = step if isinstance(step, list) else [step]

        # Single-step actions that the existing router already handles — return None
        _ROUTER_SINGLE = {"open_app", "open_website", "open_folder", "play_music", "close_app"}
        if len(steps) == 1 and steps[0]["action"] in _ROUTER_SINGLE:
            return None

        # New single-step actions we do handle ourselves
        _PLANNER_SINGLE = {"scheduled_command", "type_text", "calculate"}
        if len(steps) == 1 and steps[0]["action"] in _PLANNER_SINGLE:
            return steps

        return steps

    # Compound command — parse each part, threading context through
    all_steps: list[dict] = []
    context_site:   str | None = None
    context_folder: str | None = None

    for part in parts:
        result = _parse_single(part, context_site=context_site)
        if result is None:
            # Couldn't parse a segment → fall through to LLM
            return None
        if isinstance(result, list):
            all_steps.extend(result)
            # Update context tracking
            for s in result:
                if s["action"] == "open_website":
                    context_site = s["target"]
                elif s["action"] == "open_folder":
                    context_folder = s["target"]
        else:
            all_steps.append(result)
            if result["action"] == "open_website":
                context_site = result["target"]
            elif result["action"] == "open_folder":
                context_folder = result["target"]

    # Post-process: attach context_folder to any open_file steps that lack it
    for step in all_steps:
        if step["action"] == "open_file" and not step.get("folder"):
            step["folder"] = context_folder or "desktop"

    return all_steps if all_steps else None


# ---------------------------------------------------------------------------
# Slow path — Groq LLM
# ---------------------------------------------------------------------------

_LLM_SYSTEM = """You are the command parser for ECHO X, an AI desktop assistant.
Convert the user's command into a JSON array of action steps.
Respond ONLY with valid JSON — no explanation, no markdown.

Action types:
  {"action":"open_website",      "target":"<site_name_or_url>"}
  {"action":"open_app",          "target":"<app_name>"}
  {"action":"open_folder",       "target":"<downloads|documents|desktop|pictures>"}
  {"action":"browser_search",    "target":"<site>", "query":"<query>"}
  {"action":"play_music",        "query":"<song>"}
  {"action":"youtube_play",      "query":"<video>"}
  {"action":"close_app",         "target":"<app_name>"}
  {"action":"open_file",         "folder":"<folder>", "filename":"<file>"}
  {"action":"web_search",        "query":"<query>"}
  {"action":"scheduled_command", "time":"<HH:MMam/pm>", "command":"<command>"}
  {"action":"type_text",         "text":"<text_to_type>"}
  {"action":"calculate",         "expression":"<math_expression>"}

Rules:
- Native apps: spotify, vscode, discord, steam, notepad, calculator,
  explorer, chrome, edge, telegram, obs, task manager, control panel
- Everything else is a website (use open_website)
- "open X and search Y" → open_website(X) + browser_search(X, Y)
- "open spotify and play Y" → open_app(spotify) + play_music(Y)
- "open youtube and play Y" → open_website(youtube) + youtube_play(Y)
- "play X at 3:10pm" → scheduled_command(time=3:10pm, command=play X)
- "open notepad and type hello" → open_app(notepad) + type_text(text=hello)
- "open calculator and calculate 2+10" → open_app(calculator) + calculate(expression=2+10)
- Return [] if you cannot parse the command

Example:
User: open instagram and search cristiano
Response: [{"action":"open_website","target":"instagram"},{"action":"browser_search","target":"instagram","query":"cristiano"}]"""


def _llm_parse(command: str) -> list[dict] | None:
    """Call Groq LLM to parse a command the fast path couldn't handle."""
    try:
        resp = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": _LLM_SYSTEM},
                {"role": "user",   "content": command},
            ],
            temperature=0.0,
            max_tokens=300,
        )
        raw = resp.choices[0].message.content.strip()
        # Extract JSON array even if wrapped in markdown fences
        m = re.search(r"\[.*\]", raw, re.DOTALL)
        if m:
            steps = json.loads(m.group())
            if isinstance(steps, list) and steps:
                return steps
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(command: str) -> list[dict] | None:
    """
    Parse a natural language command into a list of action dicts.
    Returns None if the existing router should handle the command instead.

    Fast path first (regex) → LLM only if fast path returns None AND
    the command looks like a compound/automation request.
    """
    command = command.strip()
    if not command:
        return None

    # Try fast path
    steps = _fast_parse(command)
    if steps is not None:
        return steps

    # Only call LLM if command looks compound or contains automation verbs
    # (avoid LLM calls for simple "weather in delhi", "scroll up" etc.)
    if _is_compound(command) or _ACTION_VERB_RE.search(command):
        # But not if router owns it
        if not _ROUTER_OWNS.match(command):
            steps = _llm_parse(command)
            if steps:
                # Check if the parsed LLM steps is actually a single router-owned step
                _ROUTER_SINGLE = {"open_app", "open_website", "open_folder", "play_music", "close_app"}
                if len(steps) == 1 and steps[0].get("action") in _ROUTER_SINGLE:
                    return None
                return steps

    return None
