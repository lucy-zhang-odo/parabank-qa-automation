"""Test settings. Everything can be changed with environment variables."""
import os

# The public ParaBank demo by Parasoft. It is shared by everyone, so tests create their own users
# and never call endpoints that reset or change the whole site (see api.BLOCKED_PATHS).
BASE_URL = os.environ.get("PARABANK_BASE_URL", "https://parabank.parasoft.com/parabank").rstrip("/")
TIMEOUT_S = float(os.environ.get("PARABANK_TIMEOUT_S", "30"))
