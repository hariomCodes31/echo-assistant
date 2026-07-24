from playwright.sync_api import sync_playwright

browser = None
page = None

def get_browser():

    global browser, page

    if browser is None:
        browser = sync_playwright().start()
        context = browser.chromium.launch(headless=False)
        page = context.new_page()

    return page