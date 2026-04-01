"""
conftest.py — pytest's special shared-fixture file.

Any fixture defined here is automatically available to every test file in this
directory (and subdirectories) without needing an explicit import. It's the
right place for setup that is needed across multiple test modules.
"""

import os

import pytest


@pytest.fixture(autouse=True)
def nintex_env_vars(monkeypatch) -> None:
    """
    Populate the environment variables that nacwrap reads before every test.

    autouse=True means pytest runs this fixture automatically for each test —
    you don't have to list it in every test function's parameters.

    monkeypatch.setenv is preferred over os.environ[...] = ... because pytest's
    monkeypatch automatically rolls back every change after the test finishes,
    keeping tests fully isolated from one another.
    """
    if os.getenv("RUN_LIVE_API_TESTS") == "1":
        return

    monkeypatch.setenv("NINTEX_BASE_URL", "https://fake.api.nintex.example")
    monkeypatch.setenv("NTX_BEARER_TOKEN", "fake-bearer-token")
    monkeypatch.setenv("NINTEX_CLIENT_ID", "fake-client-id")
    monkeypatch.setenv("NINTEX_CLIENT_SECRET", "fake-client-secret")
    monkeypatch.setenv("NINTEX_GRANT_TYPE", "client_credentials")
    # Set an expiry far in the future so the @refresh_token decorator never
    # tries to make a real token request during tests.
    monkeypatch.setenv("NTX_BEARER_TOKEN_EXPIRES_AT", "01/01/2099 00:00:00")
