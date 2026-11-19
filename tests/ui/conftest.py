import pytest


@pytest.fixture(autouse=True)
def skip_images(page):
    """Do not download images in UI tests: fewer requests to the shared demo site, same checks."""
    page.route("**/*.{png,jpg,jpeg,gif,svg,ico}", lambda route: route.abort())
    yield
