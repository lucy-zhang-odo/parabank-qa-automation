# Findings

Behavior of the public ParaBank demo that looks like a defect. Each finding has a test marked
`xfail(strict=True)`: the test describes the expected behavior and is expected to fail today.
If ParaBank fixes the defect, the test passes unexpectedly, the run turns red, and the finding
can be closed.

ParaBank is a demo application made by Parasoft, and some of these may be intentional. They are
listed here as examples of defect reports.

| ID | Area | Expected | Actual | Test |
|---|---|---|---|---|
| F-01 | Transfer (API) | A negative amount is rejected | `amount=-5` returns 200 and money moves in the opposite direction | `test_negative_amount_is_rejected` |
| F-02 | Transfer (API) | A transfer larger than the available balance is rejected | The transfer succeeds and the account goes negative | `test_transfer_over_balance_is_rejected` |
| F-03 | Open account (API) | The `createAccount` response shows the new account's balance | The response shows `balance: 0`; reading the account right after shows the opening deposit | `test_create_account_response_shows_real_balance` |

## How they were found

Exploratory API testing before writing the automated tests: register a new user, open a second
account, then try boundary values for transfers (0.01, large amounts, negative amounts) and compare
the API response with the account balances read back from the API and the UI.
