import webbrowser
from urllib.parse import quote


def open_google():
    webbrowser.open("https://www.google.com")
    return "🌐 Opened Google"


def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "▶️ Opened YouTube"


def open_github():
    webbrowser.open("https://github.com")
    return "🐙 Opened GitHub"


def search_google(query):
    webbrowser.open(
        f"https://www.google.com/search?q={quote(query)}"
    )
    return f"🔍 Searching Google for '{query}'"


# Sites that live at root domain (no www prefix) or need a custom URL
_CUSTOM_URLS = {
    "github":    "https://github.com",
    "chatgpt":   "https://chatgpt.com",
    "claude":    "https://claude.ai",
    "gemini":    "https://gemini.google.com",
    "x":         "https://x.com",
    "twitter":   "https://x.com",
    "whatsapp":  "https://web.whatsapp.com",
    "maps":      "https://maps.google.com",
    "gmail":     "https://mail.google.com",
    "drive":     "https://drive.google.com",
    "meet":      "https://meet.google.com",
    "classroom": "https://classroom.google.com",
    "docs":      "https://docs.google.com",
    "sheets":    "https://sheets.google.com",
    "slides":    "https://slides.google.com",
    "calendar":  "https://calendar.google.com",
    "photos":    "https://photos.google.com",
    "hotstar":   "https://www.hotstar.com",
    "jio":       "https://www.jiocinema.com",
    "primevideo":"https://www.primevideo.com",
    "prime":     "https://www.primevideo.com",
}


def open_website(site: str) -> str:
    """
    Open any website by name or URL in the default browser.

    Rules:
      1. If site already contains a dot  → treat as a URL directly.
         e.g. "instagram.com" → https://www.instagram.com
              "my.company.io" → https://my.company.io
      2. Check the custom-URL map for known exceptions.
         e.g. "github"  → https://github.com
              "chatgpt" → https://chatgpt.com
      3. Fallback: prepend https://www. and append .com
         e.g. "instagram" → https://www.instagram.com
              "netflix"   → https://www.netflix.com
    """
    site = site.strip().lower()

    if "." in site:
        # User already gave a domain — just ensure it has a scheme
        url = site if site.startswith("http") else f"https://{site}"
    elif site in _CUSTOM_URLS:
        url = _CUSTOM_URLS[site]
    else:
        url = f"https://www.{site}.com"

    webbrowser.open(url)
    return f"🌐 Opening {url}"