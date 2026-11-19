from decimal import Decimal

import pytest

from parabank.money import to_decimal

pytestmark = pytest.mark.api


@pytest.mark.parametrize("amount", ["0.01", "25.50", "100"])
def test_transfer_moves_exact_amount(api, two_accounts, amount):
    customer, checking_id, savings_id = two_accounts
    amount = Decimal(amount)
    checking_before, savings_before = api.account(checking_id).balance, api.account(savings_id).balance

    r = api.transfer(checking_id, savings_id, amount)
    assert r.status_code == 200
    assert f"from account #{checking_id} to account #{savings_id}" in r.text

    assert api.account(checking_id).balance == checking_before - amount
    assert api.account(savings_id).balance == savings_before + amount


def test_transfer_keeps_total_balance(api, two_accounts):
    """Moving money between your own accounts must not change your total."""
    customer, checking_id, savings_id = two_accounts
    total_before = sum(a.balance for a in api.accounts(customer.id))
    api.transfer(savings_id, checking_id, Decimal("12.34"))
    assert sum(a.balance for a in api.accounts(customer.id)) == total_before


def test_transfer_is_recorded_on_both_accounts(api, two_accounts):
    customer, checking_id, savings_id = two_accounts
    amount = Decimal("7.77")
    api.transfer(checking_id, savings_id, amount)

    sent = [t for t in api.transactions(checking_id) if t["description"] == "Funds Transfer Sent"]
    received = [t for t in api.transactions(savings_id) if t["description"] == "Funds Transfer Received"]
    assert any(t["type"] == "Debit" and to_decimal(t["amount"]) == amount for t in sent)
    assert any(t["type"] == "Credit" and to_decimal(t["amount"]) == amount for t in received)


# --- Known defects: these document current behavior of the demo site. strict xfail means that if
# ParaBank fixes the defect, the test starts to fail, so we notice and update it. They use a
# separate customer so the defect does not change balances used by the tests above. ---

@pytest.fixture
def defect_accounts(api, fresh_customer):
    savings = api.create_account(fresh_customer.id, "SAVINGS", fresh_customer.first_account_id)
    return fresh_customer.first_account_id, savings.id


@pytest.mark.xfail(strict=True, reason="Finding F-01: a negative transfer amount is accepted (see docs/findings.md)")
def test_negative_amount_is_rejected(api, defect_accounts):
    checking_id, savings_id = defect_accounts
    r = api.transfer(checking_id, savings_id, Decimal("-5"))
    assert r.status_code == 400


@pytest.mark.xfail(strict=True, reason="Finding F-02: a transfer larger than the balance is accepted (see docs/findings.md)")
def test_transfer_over_balance_is_rejected(api, defect_accounts):
    checking_id, savings_id = defect_accounts
    r = api.transfer(checking_id, savings_id, api.account(checking_id).balance + Decimal("1000"))
    assert r.status_code == 400
