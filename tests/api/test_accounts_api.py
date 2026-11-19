import pytest

pytestmark = pytest.mark.api


def test_new_customer_has_one_checking_account(api, fresh_customer):
    accounts = api.accounts(fresh_customer.id)
    assert [a.type for a in accounts] == ["CHECKING"]
    assert accounts[0].balance > 0
    assert accounts[0].customer_id == fresh_customer.id


def test_opening_savings_account_moves_opening_deposit(api, customer):
    """Opening an account takes the opening deposit from the 'from' account. Money is moved, not created."""
    before = api.account(customer.first_account_id).balance
    new = api.create_account(customer.id, "SAVINGS", customer.first_account_id)

    savings = api.account(new.id)
    checking = api.account(customer.first_account_id)
    assert savings.type == "SAVINGS" and savings.customer_id == customer.id
    assert savings.balance > 0
    assert checking.balance == before - savings.balance
    assert new.id in {a.id for a in api.accounts(customer.id)}


@pytest.mark.xfail(strict=True, reason="Finding F-03: the createAccount response shows balance 0, "
                                       "but the account is opened with the deposit (see docs/findings.md)")
def test_create_account_response_shows_real_balance(api, customer):
    new = api.create_account(customer.id, "SAVINGS", customer.first_account_id)
    assert new.balance == api.account(new.id).balance


def test_unknown_account_returns_clear_error(api):
    r = api.get_account_raw(99999999)
    assert r.status_code == 400
    assert "Could not find account #99999999" in r.text
