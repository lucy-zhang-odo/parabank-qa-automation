import pytest
from playwright.sync_api import expect

from parabank.pages import OpenAccountPage, OverviewPage

pytestmark = pytest.mark.ui


def test_overview_matches_api_balances(logged_in_page, api, customer):
    """The UI and the API must show the same balances (UI vs. backend cross-check)."""
    api_balances = {a.id: a.balance for a in api.accounts(customer.id)}
    overview = OverviewPage(logged_in_page).open()
    assert overview.balances() == api_balances
    assert overview.total() == sum(api_balances.values())


def test_open_savings_account_from_ui(logged_in_page, api, customer):
    new_id = OpenAccountPage(logged_in_page).open().open_account("SAVINGS", customer.first_account_id)
    expect(logged_in_page.locator("#openAccountResult")).to_contain_text("Congratulations, your account is now open.")

    new = api.account(new_id)
    assert new.type == "SAVINGS" and new.customer_id == customer.id
    assert new_id in OverviewPage(logged_in_page).open().balances()
