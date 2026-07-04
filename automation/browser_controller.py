"""
browser_controller.py
---------------------
Manages a single persistent Playwright Chromium browser session.

Design decisions:
- Headed (non-headless) so the user can see execution.
- Persistent context: saves cookies/login state between runs.
- Tab reuse: if the target domain is already open, brings that tab to front
  instead of opening a new one.
- Thread-safe: protected by threading.Lock for Streamlit multi-thread access.
- State-based waits: uses Playwright's wait_for_load_state / wait_for_url,
  no fixed sleep() calls.
"""
import os
import threading
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, BrowserContext, Page, Error as PWError


# Persistent profile stored inside the project's existing chrome_profile dir
_PROFILE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "chrome_profile", "pw_profile"
)

_lock = threading.Lock()
_playwright = None
_context: BrowserContext | None = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_context() -> BrowserContext:
    """Lazily initialise the Playwright browser. Called under _lock."""
    global _playwright, _context

    # If we already have a live context, return it
    if _context is not None:
        try:
            _ = _context.pages  # Raises if context was closed
            return _context
        except Exception:
            _context = None

    os.makedirs(_PROFILE_DIR, exist_ok=True)

    _playwright = sync_playwright().start()
    _context = _playwright.chromium.launch_persistent_context(
        _PROFILE_DIR,
        headless=False,
        slow_mo=0,
        args=[
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_https_errors=True,
    )
    return _context


def _domain(url: str) -> str:
    """Extract the netloc from a URL, or return the URL itself if parsing fails."""
    try:
        return urlparse(url).netloc or url
    except Exception:
        return url


def _domains_match(d1: str, d2: str) -> bool:
    """True if two domain strings refer to the same site (handles www. prefix)."""
    d1 = d1.lstrip("www.")
    d2 = d2.lstrip("www.")
    return d1 == d2 or d1.endswith("." + d2) or d2.endswith("." + d1)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_page(url: str) -> Page:
    """
    Return a Playwright Page navigated to `url`.

    - If a tab already has the same domain open, reuses it (avoids duplicate tabs).
    - Otherwise opens a new tab.
    - Uses wait_for_load_state("domcontentloaded") — no fixed sleep.
    """
    with _lock:
        ctx = _ensure_context()
        target_domain = _domain(url)

        # Try to reuse an existing tab with the same domain
        for page in ctx.pages:
            try:
                if _domains_match(_domain(page.url), target_domain):
                    page.bring_to_front()
                    if page.url.rstrip("/") != url.rstrip("/"):
                        page.goto(url, wait_until="domcontentloaded", timeout=15_000)
                    else:
                        page.wait_for_load_state("domcontentloaded", timeout=10_000)
                    return page
            except PWError:
                continue

        # No matching tab — use the first blank page or open a new one
        blank = next(
            (p for p in ctx.pages if p.url in ("about:blank", "")),
            None
        )
        page = blank if blank else ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=15_000)
        page.bring_to_front()
        return page


def current_page() -> Page | None:
    """Return the currently focused page, or None if no browser is open."""
    with _lock:
        if _context is None:
            return None
        pages = _context.pages
        return pages[-1] if pages else None


def close():
    """Gracefully shut down the browser and Playwright instance."""
    global _playwright, _context
    with _lock:
        try:
            if _context:
                _context.close()
            if _playwright:
                _playwright.stop()
        except Exception:
            pass
        _context = None
        _playwright = None
