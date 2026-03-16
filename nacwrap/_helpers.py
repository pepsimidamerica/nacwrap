"""
Tenacity helper functions. Used for retrying requests on certain exceptions that we can expect
are temporary.
"""

import json
import logging
import os

import requests
from nacwrap._constants import PAGE_NEXT_LINK
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)
_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
    ),
)


@_basic_retry
def _make_request(
    method: str, url: str, headers: dict, context: str, **kwargs
) -> requests.Response:
    """
    Generic HTTP request handler with consistent error handling.

    Wraps requests.request() with standardized error handling,
    logging, and timeout management.

    :param method: HTTP method (GET, POST, PATCH, DELETE, etc.)
    :type method: str
    :param url: Target URL
    :type url: str
    :param headers: HTTP headers
    :type headers: dict
    :param context: Human-readable context for error messages
    :type context: str
    :param kwargs: Additional arguments passed to requests.request()
                   (json, data, params, timeout, etc.)
    :return: Response object
    :rtype: requests.Response
    :raises Exception: For HTTP errors or general request failures
    """
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            timeout=kwargs.pop("timeout", 60),
            **kwargs,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP {e.response.status_code} error, {context}: {e}")
        raise Exception(f"HTTP {e.response.status_code} error, {context}: {e}") from e
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        logger.error(f"Connection error during {context}: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during {context}: {e}")
        raise Exception(f"Request error during {context}: {e}") from e
    else:
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
        try:
            response = _make_request(
                method="GET", url=url, headers=headers, context=context, params=params
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"Pagination failed during {context}: {e}") from e

        data = response.json()
        all_results.extend(data.get(pagination_value, []))

        # Check for next page
        if PAGE_NEXT_LINK not in data:
            break

        url = data[PAGE_NEXT_LINK]

        # Commenting out. nextLink URLs seem to include params with them.
        # # Clear params for subsequent requests that use nextLink URL
        # params = None

    return all_results


@_basic_retry
def _fetch_page(url, headers, params=None, data=None) -> requests.Response:
    """
    Wrapper around requests.get that retries on certain timeout or connection-based exceptions.
    """
    response = requests.get(url, headers=headers, params=params, data=data, timeout=30)
    response.raise_for_status()
    return response


@_basic_retry
def _delete(url, headers, params=None, data=None) -> requests.Response:
    response = requests.delete(
        url, headers=headers, params=params, data=data, timeout=30
    )
    response.raise_for_status()
    return response


@_basic_retry
def _put(url, headers, params=None, data=None) -> requests.Response:
    response = requests.put(
        url, headers=headers, params=params, data=json.dumps(data), timeout=30
    )
    response.raise_for_status()
    return response


@_basic_retry
def _post(url, headers, params=None, data=None) -> requests.Response:
    response = requests.post(
        url, headers=headers, params=params, data=json.dumps(data), timeout=30
    )
    response.raise_for_status()
    return response
