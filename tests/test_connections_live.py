"""
Live contract tests for the real Nintex connections endpoint.

These tests are intentionally opt-in and should not run in CI by default.
Enable manually with RUN_LIVE_API_TESTS=1.
"""

import os

import pytest
from dotenv import load_dotenv
from nacwrap._helpers import _get_ntx_headers, _make_request

load_dotenv()

REQUIRED_ENV_VARS = [
    "NINTEX_BASE_URL",
    "NTX_BEARER_TOKEN",
]


pytestmark = pytest.mark.live_api


def _skip_unless_live_api_enabled() -> None:
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_API_TESTS=1 to run live API tests.")

    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        pytest.skip(f"Missing required env vars for live tests: {', '.join(missing)}")


def test_connections_endpoint_contract_shape() -> None:
    """
    Validate the top-level payload shape for GET /workflows/v1/connections.
    """
    _skip_unless_live_api_enabled()

    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/connections"
    response = _make_request(
        method="GET",
        url=url,
        headers=_get_ntx_headers(),
        context="live connections contract check",
    )
    payload = response.json()

    assert isinstance(payload, dict)
    assert "connections" in payload, (
        "Expected top-level key 'connections' in response payload. "
        f"Actual keys: {sorted(payload.keys())}"
    )
    assert isinstance(payload["connections"], list)


def test_connections_items_contract_shape() -> None:
    """
    Validate a minimal per-item schema when at least one connection exists.
    """
    _skip_unless_live_api_enabled()

    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/connections"
    response = _make_request(
        method="GET",
        url=url,
        headers=_get_ntx_headers(),
        context="live connections item contract check",
    )
    payload = response.json()

    connections = payload.get("connections")
    assert isinstance(connections, list)

    if not connections:
        pytest.skip(
            "No connections found in tenant; item-level contract not applicable."
        )

    first = connections[0]
    assert isinstance(first, dict)

    required_fields = {"id", "displayName"}
    missing = required_fields - set(first.keys())
    assert not missing, (
        f"Missing expected fields in connection object: {sorted(missing)}"
    )
