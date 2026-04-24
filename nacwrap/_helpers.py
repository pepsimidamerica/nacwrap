"""
Tenacity helper functions. Used for retrying requests on certain exceptions that we can expect
are temporary.
"""

import logging
import os

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

PAGE_NEXT_LINK = "nextLink"

logger = logging.getLogger(__name__)
_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before=print('HTTP request failed. Retrying...'),
    retry=retry_if_exception_type((requests.exceptions.ConnectionError, 
         requests.exceptions.Timeout, 
         requests.exceptions.RequestException, 
         requests.exceptions.HTTPError
         )
    ),
)


@_basic_retry
def _make_request(
    method: str,
    url: str,
    headers: dict,
    context: str,
    success_status_codes: list[int] | None = None,
    **kwargs,
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
    :param success_status_codes: List of status codes that are considered a successful response. If None, just returns the response to the calling function without checking the status code.
    :type success_status_codes: list[int] | None
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

    if (
        success_status_codes is not None
        and response.status_code not in success_status_codes
    ):
        logger.error(
            f"Error during {context}: {response.status_code} - {response.content}"
        )
        raise Exception(
            f"Error during {context}: {response.status_code} - {response.content}"
        )

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
