"""
Module contains functions for getting getting data source/data lookup info.
(API refers to it as datasources, but in the Nintex UI, it's data lookups)
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)


def datasources_list() -> list[dict] | None:
    """
    Get a list of Xtensions data lookups.
    """
    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/datasources"

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
            f"Error, could not get data source data: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error, could not get data source data: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get data source data: {e}")
        raise Exception(f"Error, could not get data source data: {e}")

    data = response.json()

    if "datasources" in data:
        return data["datasources"]
    else:
        return None


def datasource_connectors_list() -> list[dict] | None:
    """
    Get a list of connectors compatible with Xtensions data lookups.
    """
    url = os.environ["NINTEX_BASE_URL"] + "/workflows/v1/datasources/contracts"

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
            f"Error, could not get data source data: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"Error, could not get data source data: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get data source data: {e}")
        raise Exception(f"Error, could not get data source data: {e}")

    data = response.json()

    if "contracts" in data:
        return data["contracts"]
    else:
        return None
