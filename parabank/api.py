"""A small client for the ParaBank REST API (services/bank)."""
from dataclasses import dataclass
from decimal import Decimal

import requests

from .config import BASE_URL
from .http import PoliteSession
from .money import to_decimal

# These endpoints reset or reconfigure the whole (shared) demo site. Tests must never call them.
BLOCKED_PATHS = ("cleanDB", "initializeDB", "setParameter", "shutdownJmsListener", "startupJmsListener")


class BlockedEndpointError(RuntimeError):
    pass


@dataclass
class Account:
    id: int
    customer_id: int
    type: str
    balance: Decimal

    @classmethod
    def from_json(cls, d):
        return cls(id=d["id"], customer_id=d["customerId"], type=d["type"], balance=to_decimal(d["balance"]))


class ParaBankAPI:
    def __init__(self, base_url: str = BASE_URL):
        self.root = f"{base_url}/services/bank"
        self.http = PoliteSession()
        self.http.headers["Accept"] = "application/json"   # the API answers XML without this

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        if any(p in path for p in BLOCKED_PATHS):
            raise BlockedEndpointError(f"{path} changes the shared demo site and is not allowed in tests")
        return self.http.request(method, f"{self.root}/{path.lstrip('/')}", **kwargs)

    # --- endpoints used by the tests ---
    def login(self, username: str, password: str) -> requests.Response:
        return self.request("GET", f"login/{username}/{password}")

    def accounts(self, customer_id: int) -> list[Account]:
        r = self.request("GET", f"customers/{customer_id}/accounts")
        r.raise_for_status()
        return [Account.from_json(a) for a in r.json()]

    def account(self, account_id: int) -> Account:
        r = self.request("GET", f"accounts/{account_id}")
        r.raise_for_status()
        return Account.from_json(r.json())

    def get_account_raw(self, account_id: int) -> requests.Response:
        return self.request("GET", f"accounts/{account_id}")

    def create_account(self, customer_id: int, account_type: str, from_account_id: int) -> Account:
        type_code = {"CHECKING": 0, "SAVINGS": 1}[account_type]
        r = self.request("POST", "createAccount",
                         params={"customerId": customer_id, "newAccountType": type_code, "fromAccountId": from_account_id})
        r.raise_for_status()
        return Account.from_json(r.json())

    def transfer(self, from_id: int, to_id: int, amount) -> requests.Response:
        return self.request("POST", "transfer", params={"fromAccountId": from_id, "toAccountId": to_id, "amount": str(amount)})

    def transactions(self, account_id: int) -> list[dict]:
        r = self.request("GET", f"accounts/{account_id}/transactions")
        r.raise_for_status()
        return r.json()
