import pytest
from playwright.sync_api import expect

from parabank.data import CustomerData, register_customer
from parabank.pages import RegisterPage

pytestmark = pytest.mark.ui


def test_register_new_customer(page, api):
    data = CustomerData()
    reg = RegisterPage(page).open()
    reg.register(data)
    expect(reg.title).to_have_text(f"Welcome {data.username}")
    expect(page.locator("#rightPanel")).to_contain_text("Your account was created successfully. You are now logged in.")
    # The new customer can log in through the API too.
    assert api.login(data.username, data.password).status_code == 200


def test_register_with_mismatched_password_shows_error(page):
    reg = RegisterPage(page).open()
    reg.register(CustomerData(), repeated_password="Different-1")
    expect(reg.field_error("repeatedPassword")).to_have_text("Passwords did not match.")


def test_register_with_existing_username_shows_error(page):
    taken = register_customer()                     # create the user first (test setup)
    reg = RegisterPage(page).open()
    reg.register(CustomerData(username=taken.username))
    expect(reg.field_error("customer.username")).to_have_text("This username already exists.")


@pytest.mark.parametrize("field, message", [
    ("customer.firstName", "First name is required."),
    ("customer.lastName", "Last name is required."),
    ("customer.ssn", "Social Security Number is required."),
    ("customer.username", "Username is required."),
    ("customer.password", "Password is required."),
])
def test_register_required_field_shows_error(page, field, message):
    reg = RegisterPage(page).open()
    reg.register(CustomerData(), skip=(field,))
    expect(reg.field_error(field)).to_have_text(message)
