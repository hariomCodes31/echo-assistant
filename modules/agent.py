TOOLS = {
    "browser": [
        "open google",
        "open youtube",
        "open github",
        "search"
    ],

    "weather": [
        "weather",
        "temperature",
        "forecast"
    ],

    "sports": [
        "score",
        "match",
        "football",
        "cricket"
    ],

    "music": [
        "play",
        "song",
        "music"
    ]
}


def choose_tool(command):

    command = command.lower()

    for tool, keywords in TOOLS.items():

        for keyword in keywords:

            if keyword in command:
                return tool

    return "chat"