from tools.vision import analyze_screenshot
from tools.browser import (
    open_google,
    open_youtube,
    open_github,
    search_google,
    open_website,
)

from tools.weather import weather
from tools.desktop import desktop
from tools.music import music
from automation.planner import run as planner_run


def execute(command):

    command = command.lower().strip()

    # ---------------- Multi-step Automation Planner ---------------- #
    # Handles compound commands ("open spotify and play X", etc.).
    # Returns None to fall through to the existing routing below.
    plan_result = planner_run(command)
    if plan_result is not None:
        return plan_result

    # ---------------- Desktop ---------------- #

    result = desktop(command)

    if result:
        return result

    # ---------------- Music ---------------- #

    result = music(command)

    if result:
        return result

    # ---------------- Vision ---------------- #

    result = analyze_screenshot(command)

    if result:
        return result

    # ---------------- Browser ---------------- #

    if command == "open google":
        return open_google()

    elif command == "open youtube":
        return open_youtube()

    elif command == "open github":
        return open_github()

    elif command.startswith("search "):
        query = command.replace("search ", "")
        return search_google(query)

    # ---------------- Weather ---------------- #

    elif command.startswith("weather in"):
        return weather(command)

    # ---------------- Generic Website Opener ---------------- #
    # Triggers on: "open X", "launch X", "go to X", "navigate to X"
    # Runs last so it never shadows desktop app commands above.

    _WEB_PREFIXES = ("open ", "launch ", "go to ", "navigate to ")

    # Known desktop-app keywords that should NOT be treated as websites
    _DESKTOP_NAMES = {
        "chrome", "vscode", "vs code", "calculator", "notepad", "paint",
        "explorer", "file explorer", "spotify", "downloads", "documents",
        "desktop", "pictures", "google", "youtube", "github"
    }

    for prefix in _WEB_PREFIXES:
        if command.startswith(prefix):
            site = command[len(prefix):].strip()
            if site and site not in _DESKTOP_NAMES:
                return open_website(site)
            break

    return None


def execute_multiple(prompt):

    separators = [
        " and ",
        ",",
        " then "
    ]

    commands = [prompt]

    for sep in separators:

        temp = []

        for cmd in commands:
            temp.extend(cmd.split(sep))

        commands = temp

    responses = []

    for cmd in commands:

        cmd = cmd.strip()

        if not cmd:
            continue

        result = execute(cmd)

        if result:
            responses.append(result)

    return responses