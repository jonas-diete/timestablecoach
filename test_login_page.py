import re
from playwright.sync_api import Page, expect, sync_playwright

def test_homepage_has_correct_title(page: Page):
    page.goto("https://ttcoach.herokuapp.com/login")
    expect(page).to_have_title(re.compile("Times Table Coach"))

def test_accepting_cookies_hides_box(page: Page):
    page.goto("https://ttcoach.herokuapp.com/login")
    accept_button = page.get_by_role("button", name="Accept").click()
    # checking accept_button is None (doesn't exist)
    assert not accept_button

def test_logging_in(page: Page):
    page.goto("https://ttcoach.herokuapp.com/login")
    page.get_by_role("button", name="Accept").click()
    page.get_by_placeholder("Username").fill("Harry")
    page.get_by_placeholder("Password").fill("potter")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_text("Welcome, Harry. Select a timestable.")).to_be_visible()