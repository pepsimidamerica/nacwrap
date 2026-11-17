"""
Module for handling getting (and refreshing) the Nintex bearer token
When adding a new nacwrap function that hits the Nintex API, just add the refresh_token
decorator to it.
"""

import logging
import os
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import ParamSpec, TypeVar

import httpx2

logger = logging.getLogger(__name__)


_P = ParamSpec("_P")
_R = TypeVar("_R")


class NintexAuthError(Exception):
    """
    Raised when a Nintex bearer token cannot be obtained.
    """


class Decorators:
    """
    The Decorators class is used to define functionality for getting
    and refreshing the Nintex bearer token before each API call.
    """

    @staticmethod
    def refresh_token(decorated: Callable[_P, _R]) -> Callable[_P, _R]:
        """
        Decorator to refresh the access token if it has expired or generate
        a new one if it does not exist.

        :param decorated: The callable to decorate.
        :type decorated: Callable
        :return: The wrapped callable with token refresh logic.
        :rtype: Callable
        """

        @wraps(decorated)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            """
            A wrapper function used to check if the bearer token env vars
            need to be refreshed.
            """
            # Nintex returns ISO 8601 UTC, e.g. "2026-11-17T20:13:14.883Z".
            # Refresh a minute early so a token can't expire mid-request.
            expires_at = os.environ.get(
                "NTX_BEARER_TOKEN_EXPIRES_AT", "1901-01-01T00:00:00Z"
            )
            try:
                expired = datetime.fromisoformat(expires_at) - timedelta(
                    minutes=1
                ) < datetime.now(UTC)
            except ValueError:
                logger.warning(f"Unparseable token expiry {expires_at!r}, refreshing")
                expired = True
            if "NTX_BEARER_TOKEN" not in os.environ or expired:
                Decorators.get_token()
            return decorated(*args, **kwargs)

        return wrapper

    @staticmethod
    def get_token() -> None:
        """
        Get a new Nintex bearer token and set the corresponding environment variables.
        """
        if "NINTEX_BASE_URL" not in os.environ:
            raise NintexAuthError("NINTEX_BASE_URL not set in environment")
        if "NINTEX_CLIENT_ID" not in os.environ:
            raise NintexAuthError("NINTEX_CLIENT_ID not set in environment")
        if "NINTEX_CLIENT_SECRET" not in os.environ:
            raise NintexAuthError("NINTEX_CLIENT_SECRET not set in environment")
        if "NINTEX_GRANT_TYPE" not in os.environ:
            raise NintexAuthError("NINTEX_GRANT_TYPE not set in environment")

        response = httpx2.post(
            os.environ["NINTEX_BASE_URL"] + "/authentication/v1/token",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "client_id": os.environ["NINTEX_CLIENT_ID"],
                "client_secret": os.environ["NINTEX_CLIENT_SECRET"],
                "grant_type": os.environ["NINTEX_GRANT_TYPE"],
            },
            timeout=30,
        )
        if not response.is_success:
            msg = (
                f"Nintex token request failed ({response.status_code}): {response.text}"
            )
            logger.error(msg)
            raise NintexAuthError(msg)
        try:
            os.environ["NTX_BEARER_TOKEN"] = response.json()["access_token"]
        except Exception as e:
            logger.error(f"Error, could not set OS env bearer token: {e}")
            raise NintexAuthError(
                f"Error, could not set OS env bearer token: {e}"
            ) from e
        try:
            os.environ["NTX_BEARER_TOKEN_EXPIRES_AT"] = response.json()["expires_at"]
        except Exception as e:
            logger.error(f"Error, could not set os env expires at: {e}")
            raise NintexAuthError(f"Error, could not set os env expires at: {e}") from e
