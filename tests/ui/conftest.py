import pytest

from parabank.run_control import stop_after_this_test


@pytest.fixture(autouse=True)
def skip_images(page):
    """Do not download images in UI tests: fewer requests to the shared demo site, same checks."""
    page.route("**/*.{png,jpg,jpeg,gif,svg,ico}", lambda route: route.abort())
    yield


@pytest.fixture(autouse=True)
def stop_if_rate_limited(page, request):
    """If the browser gets HTTP 429, the test fails (usually by waiting for an element that
    never appears). Stop the run after it, so the reason is clear and no time is wasted."""
    limited = []
    page.on("response", lambda r: limited.append(r.url) if r.status == 429 else None)
    yield
    if limited:
        stop_after_this_test(request.session, f"ParaBank demo rate-limited the browser (HTTP 429 on "
                             f"{limited[0]}). Remaining tests were not run; wait and run again.")
