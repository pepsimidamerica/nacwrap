"""
Tests for nacwrap.connections.

Key ideas used throughout this file:

1.  patch() — from unittest.mock (standard library). Temporarily replaces a
    name in a module's namespace with a fake object for the duration of a
    `with` block. We patch the name as it exists *in the module under test*,
    not where it's originally defined.

    Why:  connections_list() calls _make_request(), which would hit the real
          Nintex API. By patching nacwrap.connections._make_request we intercept
          that call and return whatever we want, keeping tests fast and offline.

2.  MagicMock() — a flexible stand-in object. Calling .json() on a real
    requests.Response returns a dict; MagicMock lets us configure exactly what
    that dict looks like via `mock_response.json.return_value = {...}`.

3.  Environment variables are handled by the `nintex_env_vars` fixture in
    conftest.py (runs automatically via autouse=True).
"""

from unittest.mock import MagicMock, patch

import pytest
from nacwrap.connections import connections_list


class TestConnectionsList:
    """
    Unit tests for connections_list().
    """

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    def test_returns_list_when_connections_present(self) -> None:
        """
        When the API response contains a 'connections' key, return its value.
        """
        fake_connections = [
            {
                "id": "BLAHBLAHBLAHLONGUUIDHERE-1234-5678-90ab-cdef12345678",
                "displayName": "Pepsi",
                "isInvalid": False,
                "createdDate": "2022-02-16T22:20:50.1595825+00:00",
                "contractName": "Google Drive",
                "contractId": "abcd-1234-4567-abcd-a12cd56ef78",
                "createdByUserId": "auth0|1234567890abcdef12345678",
                "appId": "000000-8019-4c8d-9e9e-000000000",
                "contractTags": "agentic_documentloader;agentic_tools",
                "hasPublicOperation": True,
                "private": False,
                "keepAlive": True,
            },
            {
                "id": "BLAHBLAHBLAHLONGUUIDHERE-5678-1234-90ab-cdef12345678",
                "displayName": "Nick Powless",
                "isInvalid": False,
                "createdDate": "2024-10-09T18:51:05.4099516+00:00",
                "contractName": "Microsoft Exchange Online",
                "contractId": "abcd-5678-1234-abcd-a12cd56ef78",
                "createdByUserId": "auth0|1234567890abcdef12345678",
                "appId": "000000-347a-4cb9-800f-000000000",
                "contractTags": "agentic_tools",
                "hasPublicOperation": True,
                "private": False,
                "keepAlive": True,
            },
        ]
        mock_response = MagicMock()
        mock_response.json.return_value = {"connections": fake_connections}

        with patch("nacwrap.connections._make_request", return_value=mock_response):
            result = connections_list()

        assert result == fake_connections

    def test_returns_empty_list_when_connections_key_is_empty(self) -> None:
        """
        'connections' key present but empty — return an empty list, not None.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"connections": []}

        with patch("nacwrap.connections._make_request", return_value=mock_response):
            result = connections_list()

        assert result == []

    # ------------------------------------------------------------------
    # Edge-case / none-return tests
    # ------------------------------------------------------------------

    def test_returns_none_when_connections_key_absent(self) -> None:
        """
        When the API response has no 'connections' key, return None.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"someUnexpectedKey": "someValue"}

        with patch("nacwrap.connections._make_request", return_value=mock_response):
            result = connections_list()

        assert result is None

    # ------------------------------------------------------------------
    # Contract / integration-shape tests
    # ------------------------------------------------------------------

    def test_calls_correct_endpoint(self) -> None:
        """
        Verify that connections_list() hits the right URL and uses GET.

        assert_called_once_with() will fail the test if _make_request was
        called zero times, more than once, or with different arguments.
        """
        mock_response = MagicMock()
        mock_response.json.return_value = {"connections": []}

        with patch(
            "nacwrap.connections._make_request", return_value=mock_response
        ) as mock_req:
            connections_list()

        mock_req.assert_called_once_with(
            method="GET",
            url="https://fake.api.nintex.example/workflows/v1/connections",
            headers={"Authorization": "Bearer fake-bearer-token"},
            context="get connections list",
        )

    # ------------------------------------------------------------------
    # Error-propagation tests
    # ------------------------------------------------------------------

    def test_propagates_exception_from_make_request(self) -> None:
        """
        If _make_request raises (e.g. HTTP 500, timeout), the exception must
        not be silently swallowed — it should bubble up to the caller.

        pytest.raises() acts like a `with` block that *expects* an exception.
        The test fails if no exception (or a different one) is raised.
        The optional `match=` checks that the message contains that substring.
        """
        with patch(
            "nacwrap.connections._make_request",
            side_effect=Exception("HTTP 500 error, get connections list"),
        ):
            with pytest.raises(Exception, match="HTTP 500 error"):
                connections_list()
