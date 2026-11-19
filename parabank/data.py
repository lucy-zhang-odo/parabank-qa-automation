"""Test data: tests create their own customers with unique usernames, so they never depend on
shared demo data (such as the built-in john/demo user) and repeated or parallel runs do not clash."""
import secrets
import time
from dataclasses import dataclass, field

from .config import BASE_URL
from .http import PoliteSession

PASSWORD = "Test-Passw0rd"
REGISTER_OK = "Your account was created successfully"


def unique_username(prefix: str = "qa") -> str:
    # Time + random part: unique across parallel runs and CI re-runs.
    return f"{prefix}{int(time.time())}{secrets.token_hex(3)}"


@dataclass
class CustomerData:
    """Form data for the registration page. Values are fake and only used on the demo site."""
    username: str = field(default_factory=unique_username)
    password: str = PASSWORD
    first_name: str = "Test"
    last_name: str = "Customer"
    street: str = "1 Test Street"
    city: str = "Testville"
    state: str = "CA"
    zip_code: str = "90001"
    phone: str = "5550100"
    ssn: str = "000-00-0000"

    def form(self, repeated_password: str | None = None) -> dict:
        return {
            "customer.firstName": self.first_name, "customer.lastName": self.last_name,
            "customer.address.street": self.street, "customer.address.city": self.city,
            "customer.address.state": self.state, "customer.address.zipCode": self.zip_code,
            "customer.phoneNumber": self.phone, "customer.ssn": self.ssn,
            "customer.username": self.username, "customer.password": self.password,
            "repeatedPassword": self.password if repeated_password is None else repeated_password,
        }


@dataclass
class Customer:
    data: CustomerData
    id: int
    first_account_id: int

    @property
    def username(self):
        return self.data.username

    @property
    def password(self):
        return self.data.password


def register_customer(base_url: str = BASE_URL, data: CustomerData | None = None) -> CustomerData:
    """Create a customer through the registration form (ParaBank has no API for this).
    This is test setup, so it skips the browser to stay fast; the UI flow itself is tested in tests/ui."""
    data = data or CustomerData()
    s = PoliteSession()
    s.get(f"{base_url}/register.htm")          # gets a session cookie
    r = s.post(f"{base_url}/register.htm", data=data.form())
    if REGISTER_OK not in r.text:
        raise RuntimeError(f"Could not register test customer {data.username} (HTTP {r.status_code})")
    return data
