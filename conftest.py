import pytest
import requests

from parabank.api import ParaBankAPI
from parabank.config import BASE_URL, TIMEOUT_S
from parabank.data import Customer, CustomerData, register_customer
from parabank.http import RateLimitedError
from parabank.run_control import stop, stop_after_this_test


def pytest_report_header():
    return f"ParaBank: {BASE_URL}"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    yield
    if call.excinfo is not None and call.excinfo.errisinstance(RateLimitedError):
        stop_after_this_test(item.session, f"{call.excinfo.value} Remaining tests were not run.")


@pytest.fixture(scope="session", autouse=True)
def demo_site_is_up(pytestconfig):
    """Stop early with a clear message if the shared demo site is down or rate-limiting us,
    so an outage is not reported as a pile of test failures."""
    try:
        r = requests.get(f"{BASE_URL}/index.htm", timeout=TIMEOUT_S)
    except requests.RequestException as e:
        stop(pytestconfig, f"ParaBank demo site is not reachable ({e}). No tests were run.")
    if r.status_code == 429:
        stop(pytestconfig, f"ParaBank demo site is rate-limiting requests (Retry-After: {r.headers.get('Retry-After', '?')} s). "
             "No tests were run; try again later.")
    if r.status_code != 200 or "ParaBank" not in r.text:
        stop(pytestconfig, f"ParaBank demo site is not available (HTTP {r.status_code}). No tests were run.")


@pytest.fixture(scope="session")
def api() -> ParaBankAPI:
    return ParaBankAPI()


def new_customer(api) -> Customer:
    data = register_customer(data=CustomerData())
    me = api.login(data.username, data.password).json()
    accounts = api.accounts(me["id"])
    return Customer(data=data, id=me["id"], first_account_id=accounts[0].id)


@pytest.fixture
def fresh_customer(api) -> Customer:
    """A brand-new customer for a test that needs an untouched starting state."""
    return new_customer(api)


@pytest.fixture(scope="module")
def customer(api) -> Customer:
    """One new customer per test file. The demo site is shared and rate-limited, so we do not
    register a user for every test. Tests that change balances read the balances they need
    right before acting, so they do not depend on each other or on test order."""
    return new_customer(api)


@pytest.fixture(scope="module")
def two_accounts(api, customer):
    """(customer, checking id, savings id): the customer's first account plus a SAVINGS account
    opened from it. Read balances in the test itself; they change during the module."""
    savings = api.create_account(customer.id, "SAVINGS", customer.first_account_id)
    return customer, customer.first_account_id, savings.id


@pytest.fixture
def logged_in_page(page, customer):
    from parabank.pages import LoginPage
    LoginPage(page).open().login(customer.username, customer.password)
    return page
