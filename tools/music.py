import os
import webbrowser
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("YOUTUBE_API_KEY")


def music(command):

    command = command.strip()

    if not command.lower().startswith("play "):
        return None

    song = command[5:].strip()

    if not API_KEY:
        fallback_url = f"https://www.youtube.com/results?search_query={quote(song)}"
        webbrowser.open(fallback_url)
        return f"🎵 Opening YouTube search for '{song}' (YOUTUBE_API_KEY not set)"

    try:

        url = (
            "https://www.googleapis.com/youtube/v3/search"
        )

        params = {
            "part": "snippet",
            "q": song,
            "maxResults": 1,
            "type": "video",
            "key": API_KEY,
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        items = data.get("items", [])

        if not items:
            return "❌ No song found."

        video_id = items[0]["id"]["videoId"]

        youtube_url = (
            f"https://www.youtube.com/watch?v={video_id}"
        )

        webbrowser.open(youtube_url)

        return f"🎵 Playing {song}"

    except Exception as e:

        return f"❌ {e}"