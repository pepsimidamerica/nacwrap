"""
Tenacity helper functions. Used for retrying requests on certain exceptions that we can expect
are temporary.
"""

import json

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

_basic_retry = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (requests.exceptions.ConnectionError, requests.exceptions.Timeout)
    ),
)


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
