"""
Module for handling getting (and refreshing) the Nintex bearer token
When adding a new nacwrap function that hits the Nintex API, just add the refresh_token
decorator to it.
"""

import logging
import os
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import ParamSpec, TypeVar

import requests

logger = logging.getLogger(__name__)


_P = ParamSpec("_P")
_R = TypeVar("_R")


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
            if "NTX_BEARER_TOKEN_EXPIRES_AT" not in os.environ:
                expires_at = "01/01/1901 00:00:00"
            else:
                expires_at = os.environ["NTX_BEARER_TOKEN_EXPIRES_AT"]
            if (
                "NTX_BEARER_TOKEN" not in os.environ
                or datetime.strptime(expires_at, "%m/%d/%Y %H:%M:%S") < datetime.now()
            ):
                Decorators.get_token()
            return decorated(*args, **kwargs)

        return wrapper

    @staticmethod
    def get_token() -> None:
        """
        Get a new Nintex bearer token and set the corresponding environment variables.
        """
        if "NINTEX_BASE_URL" not in os.environ:
            raise Exception("NINTEX_BASE_URL not set in environment")
        if "NINTEX_CLIENT_ID" not in os.environ:
            raise Exception("NINTEX_CLIENT_ID not set in environment")
        if "NINTEX_CLIENT_SECRET" not in os.environ:
            raise Exception("NINTEX_CLIENT_SECRET not set in environment")
        if "NINTEX_GRANT_TYPE" not in os.environ:
            raise Exception("NINTEX_GRANT_TYPE not set in environment")

        response = requests.post(
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
        try:
            os.environ["NTX_BEARER_TOKEN"] = response.json()["access_token"]
        except Exception as e:
            logger.error(f"Error, could not set OS env bearer token: {e}")
            raise Exception(f"Error, could not set OS env bearer token: {e}") from e
        try:
            os.environ["NTX_EXPIRES_AT"] = response.json()["expires_at"]
        except Exception as e:
            logger.error(f"Error, could not set os env expires at: {e}")
            raise Exception(f"Error, could not set os env expires at: {e}") from e
