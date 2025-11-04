"""
Module contains function for getting connection info
"""

import logging
import os

import requests
from nacwrap._auth import Decorators
from nacwrap._helpers import _basic_retry

logger = logging.getLogger(__name__)


@_basic_retry
@Decorators.refresh_token
def connections_list() -> list[dict] | None:
    """
    Get a list of Xtensions connections.
    """
    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/connections"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"Error, could not get connection data: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error, could not get connection data: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get connection data: {e}")
        raise Exception(f"Error, could not get connection data: {e}")

    data = response.json()

    if "connections" in data:
        return data["connections"]
    else:
        return None
