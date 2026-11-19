# ParaBank QA Automation

[![tests](https://github.com/lucy-zhang-odo/parabank-qa-automation/actions/workflows/tests.yml/badge.svg)](https://github.com/lucy-zhang-odo/parabank-qa-automation/actions/workflows/tests.yml)

UI and API test automation for [ParaBank](https://parabank.parasoft.com/parabank/), a public demo
online bank by Parasoft. Built with **Python, pytest, and Playwright**, and run in **GitHub Actions**.

[中文說明](README.zh-TW.md)

## What is tested

| Area | UI (Playwright) | API (REST) |
|---|---|---|
| Login / logout | valid login, wrong password, empty fields, pages closed after logout | valid login returns the customer, wrong password returns 400 |
| Registration | new customer, password mismatch, existing username, required fields | – |
| Accounts | overview balances match the API, open a savings account | one checking account for a new customer, opening deposit is moved (not created), unknown account |
| Transfer | transfer from the UI, then check balances (API) and account activity (UI) | exact amounts (0.01 / 25.50 / 100), total balance unchanged, transactions on both accounts |
| Known defects | – | 3 findings, see [docs/findings.md](docs/findings.md) |

## Test design

- **Own test data.** Tests register their own customers with unique usernames. They never use the
  shared demo user (john/demo), so other people's activity on the demo site cannot break them.
- **UI checked against the backend.** After a UI action (open account, transfer), the test reads the
  result from the API too, so a page that *looks* right but saved the wrong data still fails.
- **Money as Decimal.** Amounts are compared as `Decimal`, never as floats.
- **Known defects as strict expected failures.** Each finding is a test that describes the correct
  behavior. If ParaBank fixes it, the test fails on purpose so the finding can be closed.
- **Polite to a shared site.** The demo site is public and rate-limited, so the tests:
  - create one customer per test file instead of one per test,
  - skip image downloads in the browser and pause briefly between API requests,
  - stop with a clear message on HTTP 429 or when the site is down, instead of reporting many failures,
  - can never call the endpoints that reset the whole site (`cleanDB`, `initializeDB`, ...).
- **Page Object Model.** Selectors live in `parabank/pages.py`; tests only describe what they check.

## Project structure

```
parabank/            test framework
  api.py             REST API client (blocks site-wide reset endpoints)
  pages.py           page objects
  data.py            test data: unique customers, registration
  http.py            request pacing and rate-limit handling
  money.py           amount parsing
tests/api/           API tests
tests/ui/            browser tests
docs/findings.md     defects found by exploratory testing
tools/               CI summary script
.github/workflows/   GitHub Actions
```

## Run locally

Requires Python 3.12 or later.

```bash
pip install -r requirements.txt
python -m playwright install chromium

pytest -m api                      # API tests only
pytest -m ui                       # UI tests (headless)
pytest -m ui --headed              # watch the browser
pytest --html=reports/report.html --self-contained-html
```

Set `PARABANK_BASE_URL` to test another ParaBank installation, for example a local Docker container
(`docker run -p 8080:8080 parasoft/parabank`, then `PARABANK_BASE_URL=http://localhost:8080/parabank`).

## CI

GitHub Actions runs API tests, then UI tests, on every push to `main`, on pull requests, every Monday,
and on demand. Each run shows a result table in the job summary and uploads the HTML reports and
Playwright traces of failed tests as an artifact. Only one run at a time, to keep the load on the
demo site low.

## Notes

ParaBank is made and hosted by [Parasoft](https://www.parasoft.com/) for testing practice. Test data
is fake. Because the site is shared, a run can occasionally fail for reasons outside the tests
(slow responses, site resets); the CI log says when the site was unavailable.
