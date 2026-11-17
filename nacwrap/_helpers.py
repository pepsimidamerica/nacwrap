"""
Tenacity helper functions. Used for retrying requests on certain exceptions that we can expect
are temporary.
"""

import logging
import os

import httpx2
from tenacity import (
    RetryCallState,
    retry,
    stop_after_attempt,
    wait_exponential,
)

from nacwrap.exceptions import WorkflowApiError

PAGE_NEXT_LINK = "nextLink"
IDEMPOTENT_METHODS = {"GET", "HEAD", "OPTIONS", "PUT", "DELETE"}
RETRY_STATUS_CODES = {500, 502, 503, 504}

logger = logging.getLogger(__name__)


def _should_retry(retry_state: RetryCallState) -> bool:
    """
    Decide whether a failed _make_request call is safe to retry.

    Anything that failed before the request reached Nintex (connection errors,
    connect/pool timeouts, 429) is always retried. Failures where Nintex may have
    already acted on the request (read/write timeouts, 5xx) are only retried for
    idempotent methods, so e.g. a timed out POST never creates a duplicate instance.

    :param retry_state: Tenacity state for the current call.
    :type retry_state: RetryCallState
    :return: True if the call should be retried.
    :rtype: bool
    """
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    if exc is None:
        return False

    method = retry_state.kwargs.get("method") or retry_state.args[0]
    idempotent = method.upper() in IDEMPOTENT_METHODS

    if isinstance(
        exc, (httpx2.ConnectError, httpx2.ConnectTimeout, httpx2.PoolTimeout)
    ):
        return True
    if isinstance(exc, (httpx2.NetworkError, httpx2.TimeoutException)):
        return idempotent
    if isinstance(exc, WorkflowApiError):
        return exc.status_code == 429 or (
            idempotent and exc.status_code in RETRY_STATUS_CODES
        )
    return False


# ignores Retry-After on 429
_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=_should_retry,
    reraise=True,
)


@_basic_retry
def _make_request(
    method: str,
    url: str,
    headers: dict,
    context: str,
    success_status_codes: list[int] | None = None,
    **kwargs,
) -> httpx2.Response:
    """
    Generic HTTP request handler with consistent error handling.

    Wraps httpx2.request() with standardized error handling,
    logging, and timeout management.

    :param method: HTTP method (GET, POST, PATCH, DELETE, etc.)
    :type method: str
    :param url: Target URL
    :type url: str
    :param headers: HTTP headers
    :type headers: dict
    :param context: Human-readable context for error messages
    :type context: str
    :param success_status_codes: List of status codes that are considered a successful response. If None, just returns the response to the calling function without checking the status code.
    :type success_status_codes: list[int] | None
    :param kwargs: Additional arguments passed to httpx2.request()
                   (json, data, params, timeout, etc.)
    :return: Response object
    :rtype: httpx2.Response
    :raises WorkflowApiError: For HTTP error statuses or general request failures
    :raises httpx2.NetworkError: For connection failures, after retries
    :raises httpx2.TimeoutException: For timeouts, after retries
    """
    try:
        response = httpx2.request(
            method,
            url,
            headers=headers,
            timeout=kwargs.pop("timeout", 60),
            follow_redirects=True,
            **kwargs,
        )
        response.raise_for_status()
    except httpx2.HTTPStatusError as e:
        msg = f"HTTP {response.status_code} error, {context}: {e}"
        logger.error(msg)
        raise WorkflowApiError(msg, status_code=response.status_code) from e
    except (httpx2.NetworkError, httpx2.TimeoutException) as e:
        logger.error(f"Connection error during {context}: {e}")
        raise
    except httpx2.HTTPError as e:
        msg = f"Request error during {context}: {e}"
        logger.error(msg)
        raise WorkflowApiError(msg) from e

    if (
        success_status_codes is not None
        and response.status_code not in success_status_codes
    ):
        msg = f"Error during {context}: {response.status_code} - {response.content}"
        logger.error(msg)
        raise WorkflowApiError(msg, status_code=response.status_code)

    return response


def _get_ntx_headers(extra_headers: dict | None = None) -> dict:
    """
    Returns Nintex API headers with bearer token.

    :param extra_headers: Additional headers to merge in
    :type extra_headers: dict | None
    :return: Complete headers dict for Graph API requests
    :rtype: dict
    """
    headers = {"Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"]}
    if extra_headers:
        headers.update(extra_headers)
    return headers


def _get_paginated(
    url: str,
    pagination_value: str,
    headers: dict,
    params: dict | None = None,
    context: str = "API request",
) -> list[dict]:
    """
    Fetches paginated results from a Nintex API endpoint.

    Automatically handles nextLink pagination and applies
    retry logic to handle transient failures.

    :param url: The initial API endpoint URL
    :type url: str
    :param headers: HTTP headers including Authorization
    :type headers: dict
    :param params: Optional query parameters
    :type params: dict | None
    :param context: Description for logging (e.g., "get lists", "fetch users")
    :type context: str
    :return: Flattened list of all results across pages
    :rtype: list[dict]
    """
    all_results = []

    while True:
        response = _make_request(
            method="GET", url=url, headers=headers, context=context, params=params
        )

        data = response.json()
        all_results.extend(data.get(pagination_value, []))

        # Check for next page
        if PAGE_NEXT_LINK not in data:
            break

        url = data[PAGE_NEXT_LINK]

        # Clear params for subsequent requests that use nextLink URL
        params = None

    return all_results


def _check_env(key: str, default: str | None = None) -> str:
    """
    Checks if a given env var has been set. Raises an error if it hasn't been
    with instructions to read the README..md for setup instructions.

    :param key: The environment variable key to check
    :type key: str
    :param default: Optional default value if the env var is not set
    :type default: str | None
    :return: The value of the environment variable
    :rtype: str
    :raises OSError: If the environment variable is not set and no default is provided
    """
    value = os.environ.get(key, default)
    if value is None:
        raise OSError(
            f"Missing required environment variable: {key}\n"
            f"Please see README.md for configuration instructions."
        )
    return value
