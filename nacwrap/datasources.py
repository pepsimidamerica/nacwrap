"""
Module contains functions for getting getting data source/data lookup info.
The API refers to it as "datasources", but in the Nintex UI, it's "data lookups" Not
sure on the terminology.
"""

import logging
import os

from nacwrap._helpers import _get_ntx_headers, _make_request

logger = logging.getLogger(__name__)


def datasources_list() -> list[dict] | None:
    """
    Get a list of Xtensions data lookups.
    """
    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/datasources"

    response = _make_request(
        method="GET",
        url=url,
        headers=_get_ntx_headers(),
        context="get datasources list",
    )

    data = response.json()

    if "datasources" in data:
        return data["datasources"]

    return None


def datasource_connectors_list() -> list[dict] | None:
    """
    Get a list of connectors compatible with Xtensions data lookups.
    """
    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/datasources/contracts"

    response = _make_request(
        method="GET",
        url=url,
        headers=_get_ntx_headers(),
        context="get datasource connectors list",
    )

    data = response.json()

    if "contracts" in data:
        return data["contracts"]

    return None
