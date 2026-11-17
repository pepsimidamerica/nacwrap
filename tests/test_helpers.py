"""
Tests for the retry policy in nacwrap._helpers._make_request.

httpx2.request is patched so nothing hits the network, and the tenacity wait is
swapped for wait_none() so retries happen instantly.
"""

from unittest.mock import patch

import httpx2
import pytest
from tenacity import wait_none

from nacwrap._helpers import _make_request
from nacwrap.exceptions import WorkflowApiError

_REQ = httpx2.Request("GET", "https://fake.api.nintex.example")


def _status(code: int) -> httpx2.Response:
    """
    Build a response with the given status code.

    :param code: HTTP status code.
    :type code: int
    :return: Response attached to a dummy request.
    :rtype: httpx2.Response
    """
    return httpx2.Response(code, request=_REQ)


@pytest.mark.parametrize(
    ("method", "outcome", "expected_calls", "expected_exc"),
    [
        # Never reached Nintex, always safe to retry.
        ("POST", httpx2.ConnectError("x"), 5, httpx2.ConnectError),
        ("POST", httpx2.ConnectTimeout("x"), 5, httpx2.ConnectTimeout),
        ("POST", _status(429), 5, WorkflowApiError),
        # Nintex may have acted on it, only retry idempotent methods.
        ("GET", httpx2.ReadTimeout("x"), 5, httpx2.ReadTimeout),
        ("POST", httpx2.ReadTimeout("x"), 1, httpx2.ReadTimeout),
        ("PATCH", httpx2.ReadTimeout("x"), 1, httpx2.ReadTimeout),
        ("GET", _status(503), 5, WorkflowApiError),
        ("POST", _status(503), 1, WorkflowApiError),
        # Client errors are never retried.
        ("GET", _status(404), 1, WorkflowApiError),
    ],
)
def test_retry_policy(method, outcome, expected_calls, expected_exc) -> None:
    """
    Check how many attempts each failure gets and that the original error surfaces.
    """
    make_request = _make_request.retry_with(wait=wait_none())
    kwargs = (
        {"side_effect": outcome}
        if isinstance(outcome, Exception)
        else {"return_value": outcome}
    )

    with (
        patch("nacwrap._helpers.httpx2.request", **kwargs) as mock_request,
        pytest.raises(expected_exc),
    ):
        make_request(method, "https://fake.api.nintex.example", {}, "test")

    assert mock_request.call_count == expected_calls
