import pytest
from playwright.sync_api import expect

from parabank.pages import LoginPage, OverviewPage

pytestmark = pytest.mark.ui


def test_login_opens_accounts_overview(page, customer):
    LoginPage(page).open().login(customer.username, customer.password)
    overview = OverviewPage(page)
    expect(overview.title).to_have_text("Accounts Overview")
    expect(page.locator("#leftPanel")).to_contain_text(f"Welcome {customer.data.first_name} {customer.data.last_name}")


def test_login_with_wrong_password_shows_error(page, customer):
    login = LoginPage(page).open()
    login.login(customer.username, "wrong-password")
    expect(login.title).to_have_text("Error!")
    expect(login.errors).to_have_text("The username and password could not be verified.")


def test_login_with_empty_fields_shows_error(page):
    login = LoginPage(page).open()
    login.login("", "")
    expect(login.errors).to_have_text("Please enter a username and password.")


def test_logout_returns_to_login_form(logged_in_page):
    login = LoginPage(logged_in_page)
    login.logout()
    expect(login.login_form).to_be_visible()
    # After logout, account pages must not be reachable.
    OverviewPage(logged_in_page).open()
    expect(login.errors).to_be_visible()
