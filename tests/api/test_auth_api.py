import pytest

pytestmark = pytest.mark.api


def test_login_returns_the_customer(api, customer):
    r = api.login(customer.username, customer.password)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == customer.id
    assert (body["firstName"], body["lastName"]) == (customer.data.first_name, customer.data.last_name)
    assert body["address"]["city"] == customer.data.city


@pytest.mark.parametrize("password", ["wrong-password", "Test-passw0rd"], ids=["wrong", "wrong-case"])
def test_login_with_wrong_password_is_rejected(api, customer, password):
    r = api.login(customer.username, password)
    assert r.status_code == 400
    assert "Invalid username and/or password" in r.text


def test_blocked_endpoints_are_never_called(api):
    """Guard rail: endpoints that reset the shared demo site cannot be called by mistake."""
    from parabank.api import BlockedEndpointError
    with pytest.raises(BlockedEndpointError):
        api.request("POST", "cleanDB")
