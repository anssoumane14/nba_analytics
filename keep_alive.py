"""Keep the Streamlit Community Cloud app awake.

Opens the live app in a real headless browser (plain HTTP pings and empty
commits do not wake a sleeping Streamlit app), clicks the wake-up button if the
app is asleep, then checks that the app really rendered.

Streamlit Cloud renders the app inside an iframe (/~/+/), so every check below
looks in all frames of the page, not only the main one.

Exits with an error (so GitHub Actions marks the run red and emails you) when the
app is still asleep, shows an error page, or did not render.
"""
import sys
from playwright.sync_api import sync_playwright

URL = "https://nba-analytics-a14.streamlit.app/"
WAKE_BUTTON = "Yes, get this app back up!"


def count_in_frames(page, make_locator):
    total = 0
    for frame in page.frames:
        try:
            total += make_locator(frame).count()
        except Exception:
            pass  # a frame can detach while we look at it
    return total


def wake_buttons(page):
    return count_in_frames(page, lambda f: f.get_by_role("button", name=WAKE_BUTTON))


def app_rendered(page):
    return count_in_frames(page, lambda f: f.locator('[data-testid="stApp"]'))


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(10_000)

    if wake_buttons(page) > 0:
        print("App was asleep: clicking wake button.")
        for frame in page.frames:
            btn = frame.get_by_role("button", name=WAKE_BUTTON)
            if btn.count() > 0:
                btn.first.click()
                break
        page.wait_for_timeout(90_000)  # boot time
    else:
        print("App already awake.")

    # Give the app a little more time to render if it is not there yet.
    for _ in range(6):
        if app_rendered(page) > 0:
            break
        page.wait_for_timeout(5_000)

    ok = app_rendered(page) > 0
    asleep = wake_buttons(page) > 0
    error = count_in_frames(page, lambda f: f.get_by_text("Oh no")) > 0
    exception = count_in_frames(page, lambda f: f.locator('[data-testid="stException"]')) > 0
    page.screenshot(path="screenshot.png", full_page=True)
    browser.close()

print(f"rendered={ok} asleep={asleep} error_page={error} python_exception={exception}")
if asleep or error or exception or not ok:
    sys.exit("App is not healthy (asleep, error page, exception, or not rendered).")
print("App healthy.")
