from decimal import Decimal

import pytest
from playwright.sync_api import expect

from parabank.pages import ActivityPage, TransferPage

pytestmark = pytest.mark.ui


def test_transfer_from_ui_updates_balances_and_activity(logged_in_page, api, two_accounts):
    customer, checking_id, savings_id = two_accounts
    amount = Decimal("15.25")
    checking_before, savings_before = api.account(checking_id).balance, api.account(savings_id).balance

    transfer = TransferPage(logged_in_page).open()
    transfer.transfer(str(amount), checking_id, savings_id)
    expect(transfer.title).to_have_text("Transfer Complete!")
    assert transfer.result_values() == (amount, checking_id, savings_id)

    # Backend check: balances moved by exactly the amount.
    assert api.account(checking_id).balance == checking_before - amount
    assert api.account(savings_id).balance == savings_before + amount

    # The receiving account's activity page shows the transfer and the new balance.
    activity = ActivityPage(logged_in_page).open_for(savings_id)
    assert activity.balance() == savings_before + amount
    assert any(t["description"] == "Funds Transfer Received" and t["credit"] == f"${amount}"
               for t in activity.transactions())


def test_transfer_with_empty_amount_shows_error(logged_in_page, two_accounts):
    customer, checking_id, savings_id = two_accounts
    transfer = TransferPage(logged_in_page).open()
    transfer.transfer("", checking_id, savings_id)
    expect(transfer.errors.first).to_be_visible()
    expect(transfer.result).to_be_hidden()
