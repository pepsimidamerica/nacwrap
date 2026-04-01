"""
Module contains function for getting connection info. Connections are set up whenever you are
connecting to a given service for the first time. Third-party connections or custom xtensions.
"""

import logging
import os

from nacwrap._auth import Decorators
from nacwrap._helpers import _get_ntx_headers, _make_request
from nacwrap.data_model import Connection

logger = logging.getLogger(__name__)


@Decorators.refresh_token
def connections_list() -> list[Connection] | None:
    """
    Get a list of Xtensions connections.
    """
    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/connections"

    response = _make_request(
        method="GET",
        url=url,
        headers=_get_ntx_headers(),
        context="get connections list",
    )

    data = response.json()

    if "connections" in data:
        return [Connection(**conn) for conn in data["connections"]]

    return None
