import re
from playwright.sync_api import Page, expect


def test_homepage_has_correct_title(page: Page):
    page.goto("http://127.0.0.1:5000")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Times Table Coach"))

def test_accepting_cookies_hides_box(page: Page):
    page.goto("http://127.0.0.1:5000")
    accept_button = page.get_by_role("button", name="Accept").click()
    # checking accept_button is None (doesn't exist)
    assert not accept_button