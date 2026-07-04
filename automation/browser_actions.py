"""
browser_actions.py
------------------
High-level browser actions built on browser_controller.
Handles site opening, search, click, scroll — all with state-based waits.

URL resolution reuses the _CUSTOM_URLS map from tools/browser.py
to keep a single source of truth.
"""
from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PWTimeout

from automation import browser_controller
from tools.browser import _CUSTOM_URLS  # Reuse existing URL map


# ---------------------------------------------------------------------------
# URL resolution
# ---------------------------------------------------------------------------

def resolve_url(site: str) -> str:
    """
    Convert a site name (or partial URL) to a full https:// URL.

    Priority:
      1. Already a full URL → return as-is
      2. Contains a dot → treat as domain
      3. In custom map → use mapped URL
      4. Fallback → https://www.<site>.com
    """
    site = site.strip().lower()
    if site.startswith("http://") or site.startswith("https://"):
        return site
    if "." in site:
        return f"https://{site}"
    if site in _CUSTOM_URLS:
        return _CUSTOM_URLS[site]
    return f"https://www.{site}.com"


# ---------------------------------------------------------------------------
# Search selectors — ordered from most-specific to most-generic
# ---------------------------------------------------------------------------

_SEARCH_SELECTORS = [
    # Platform-specific
    'input[name="search_query"]',           # YouTube
    'input[id="twotabsearchtextbox"]',      # Amazon
    'input[name="field-keywords"]',          # Amazon fallback
    'input[id="query-builder-test"]',       # GitHub active input
    'button.header-search-button',          # GitHub search trigger button
    '[data-testid="site-search-input"]',     # GitHub fallback
    'input[name="q"]',                       # Google / GitHub / Flipkart
    # HTML5 standard
    'input[type="search"]',
    # Attribute-based
    'input[name="search"]',
    'input[aria-label*="search" i]',
    'input[placeholder*="search" i]',
    'button[aria-label*="search" i]',
    'a[aria-label*="search" i]',
    # CSS class based
    '#search-input',
    '.search-input',
    'input[class*="search" i]',
    # Contenteditable (WhatsApp / Notion / Slack)
    'div[contenteditable="true"][aria-label*="search" i]',
    'div[role="textbox"][aria-placeholder*="search" i]',
]

_SELECTOR_TIMEOUT_MS = 1_500  # Per-selector timeout (state-based, not fixed wait)
_LOAD_TIMEOUT_MS     = 10_000


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def open_site(site: str) -> Page:
    """
    Resolve `site` to a URL and open it in the persistent Playwright browser.
    Returns the live Page object for further actions.
    """
    url = resolve_url(site)
    return browser_controller.get_page(url)


def search_on_site(page: Page, query: str) -> bool:
    """
    Locate the search box on `page`, type `query`, and submit.

    Strategy (in order):
      1. Try each selector in _SEARCH_SELECTORS — wait_for_selector (state-based)
      2. Keyboard shortcut '/' (universal search shortcut — GitHub, YouTube, Reddit…)
      3. Keyboard shortcut 'Ctrl+K' (Chrome / VS Code style search)

    Returns True if a search was successfully submitted.
    """
    for selector in _SEARCH_SELECTORS:
        try:
            el = page.wait_for_selector(
                selector,
                timeout=_SELECTOR_TIMEOUT_MS,
                state="visible"
            )
            if el:
                tag_name = el.evaluate("el => el.tagName.toLowerCase()")
                is_editable = el.evaluate("el => el.contentEditable === 'true' || el.hasAttribute('contenteditable')")
                if tag_name in ("input", "textarea") or is_editable:
                    el.click()
                    try:
                        el.select_text()
                    except Exception:
                        pass
                    el.fill(query)
                    el.press("Enter")
                    try:
                        page.wait_for_load_state("networkidle", timeout=_LOAD_TIMEOUT_MS)
                    except PWTimeout:
                        pass
                    return True
                else:
                    # Click search button/trigger, then wait for input
                    try:
                        el.click()
                        # Search specifically for one of our known search inputs that should now be visible
                        for sub_sel in _SEARCH_SELECTORS:
                            if "button" in sub_sel or "a[" in sub_sel:
                                continue
                            try:
                                focused = page.wait_for_selector(sub_sel, timeout=1000, state="visible")
                                if focused:
                                    focused.click()
                                    try:
                                        focused.select_text()
                                    except Exception:
                                        pass
                                    focused.fill(query)
                                    focused.press("Enter")
                                    try:
                                        page.wait_for_load_state("networkidle", timeout=_LOAD_TIMEOUT_MS)
                                    except PWTimeout:
                                        pass
                                    return True
                            except Exception:
                                continue
                    except Exception:
                        pass
        except (PWTimeout, Exception):
            continue

    # Fallback 1: '/' keyboard shortcut
    try:
        page.keyboard.press("/")
        focused = page.wait_for_selector("input:focus", timeout=2_000, state="visible")
        if focused:
            focused.fill(query)
            focused.press("Enter")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=_LOAD_TIMEOUT_MS)
            except PWTimeout:
                pass
            return True
    except Exception:
        pass

    # Fallback 2: Ctrl+K
    try:
        page.keyboard.press("Control+k")
        focused = page.wait_for_selector("input:focus", timeout=2_000, state="visible")
        if focused:
            focused.fill(query)
            focused.press("Enter")
            try:
                page.wait_for_load_state("domcontentloaded", timeout=_LOAD_TIMEOUT_MS)
            except PWTimeout:
                pass
            return True
    except Exception:
        pass

    return False


def click_element(page: Page, selector: str, timeout_ms: int = 5_000) -> bool:
    """Click an element identified by `selector`. Returns True on success."""
    try:
        el = page.wait_for_selector(selector, timeout=timeout_ms, state="visible")
        if el:
            el.click()
            return True
    except Exception:
        pass
    return False


def scroll_page(page: Page, direction: str = "down", amount: int = 600) -> None:
    """Scroll the page up or down by `amount` pixels."""
    delta = amount if direction == "down" else -amount
    page.mouse.wheel(0, delta)
