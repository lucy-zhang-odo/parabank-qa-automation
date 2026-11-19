"""Page objects. Tests describe *what* they check; selectors live only here."""
from decimal import Decimal

from playwright.sync_api import Page, expect

from .config import BASE_URL
from .data import CustomerData
from .money import parse_ui_amount


class BasePage:
    path = ""

    def __init__(self, page: Page, base_url: str = BASE_URL):
        self.page = page
        self.base_url = base_url

    def open(self):
        self.page.goto(f"{self.base_url}/{self.path}")
        return self

    @property
    def title(self):
        # Several hidden panels share the "title" class; take the visible one.
        return self.page.locator("#rightPanel h1.title:visible").first

    @property
    def errors(self):
        return self.page.locator("#rightPanel .error:visible")


class LoginPage(BasePage):
    path = "index.htm"

    def login(self, username: str, password: str):
        form = self.page.locator("form[name=login]")
        form.locator("input[name=username]").fill(username)
        form.locator("input[name=password]").fill(password)
        form.locator("input[type=submit]").click()

    def logout(self):
        self.page.get_by_role("link", name="Log Out").click()

    @property
    def login_form(self):
        return self.page.locator("form[name=login]")


class RegisterPage(BasePage):
    path = "register.htm"

    def register(self, data: CustomerData, repeated_password: str | None = None, skip: tuple[str, ...] = ()):
        """Fill the form. Field names in `skip` are left empty."""
        for name, value in data.form(repeated_password).items():
            if name not in skip:
                self.page.locator(f"[id='{name}']").fill(value)
        self.page.locator("#customerForm input[type=submit]").click()

    def field_error(self, name: str):
        return self.page.locator(f"[id='{name}.errors']")


class OverviewPage(BasePage):
    path = "overview.htm"

    def wait_loaded(self):
        expect(self.page.locator("#accountTable tbody a").first).to_be_visible()
        return self

    def balances(self) -> dict[int, Decimal]:
        """{account id: balance} from the table (the 'Total' row is skipped)."""
        self.wait_loaded()
        result = {}
        for row in self.page.locator("#accountTable tbody tr").all():
            link = row.locator("a")
            if link.count():
                result[int(link.inner_text())] = parse_ui_amount(row.locator("td").nth(1).inner_text())
        return result

    def total(self) -> Decimal:
        self.wait_loaded()
        return parse_ui_amount(self.page.locator("#accountTable tbody tr", has_text="Total").locator("td").nth(1).inner_text())


class OpenAccountPage(BasePage):
    path = "openaccount.htm"

    def open_account(self, account_type: str, from_account_id: int) -> int:
        self.page.locator("#type").select_option(label=account_type)
        # The "from" list is filled by JavaScript after the page loads.
        expect(self.page.locator(f"#fromAccountId option[value='{from_account_id}']")).to_be_attached()
        self.page.locator("#fromAccountId").select_option(str(from_account_id))
        self.page.locator("input[value='Open New Account']").click()
        new_id = self.page.locator("#newAccountId")
        expect(new_id).to_be_visible()
        return int(new_id.inner_text())


class TransferPage(BasePage):
    path = "transfer.htm"

    def transfer(self, amount: str, from_id: int, to_id: int):
        expect(self.page.locator(f"#toAccountId option[value='{to_id}']")).to_be_attached()
        self.page.locator("#amount").fill(amount)
        self.page.locator("#fromAccountId").select_option(str(from_id))
        self.page.locator("#toAccountId").select_option(str(to_id))
        self.page.locator("#transferForm input[type=submit]").click()

    @property
    def result(self):
        return self.page.locator("#showResult")

    def result_values(self) -> tuple[Decimal, int, int]:
        expect(self.result).to_be_visible()
        return (parse_ui_amount(self.page.locator("#amountResult").inner_text()),
                int(self.page.locator("#fromAccountIdResult").inner_text()),
                int(self.page.locator("#toAccountIdResult").inner_text()))


class ActivityPage(BasePage):
    def open_for(self, account_id: int):
        self.page.goto(f"{self.base_url}/activity.htm?id={account_id}")
        expect(self.page.locator("#accountId")).to_have_text(str(account_id))
        return self

    def balance(self) -> Decimal:
        return parse_ui_amount(self.page.locator("#balance").inner_text())

    def transactions(self) -> list[dict]:
        """Rows of the transaction table: date, description, debit, credit."""
        expect(self.page.locator("#transactionTable tbody tr").first).to_be_visible()
        rows = []
        for row in self.page.locator("#transactionTable tbody tr").all():
            cells = [c.inner_text().strip() for c in row.locator("td").all()]
            if len(cells) >= 4:
                rows.append({"date": cells[0], "description": cells[1], "debit": cells[2], "credit": cells[3]})
        return rows
