import os
from enum import Enum
from datetime import date, datetime
from typing import Literal, Optional, Union, List
import requests
from pprint import pprint
from pydantic import BaseModel, Field

from nacwrap._auth import Decorators
from nacwrap._helpers import _fetch_page
from nacwrap.data_model import *

"""
This module contains functions relating to user management.
"""


@Decorators.refresh_token
def users_list(
    id: str = None,
    email: str = None,
    filter: str = None,
    role: str = None,
) -> List[NintexUser]:
    """
    Get Nintex User Data.
    Returns: List of NintexUser pydantic objects.

    :param id: User's ID filter
    :param email: User's email filter
    :param filter: User's name or email filter
    :param role: User's role filter
    """
    base_url = os.environ["NINTEX_BASE_URL"] + "/tenants/v1/users"
    params = {"id": id, "email": email, "filter": filter, "role": role}

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    results: List[NintexUser] = []
    url = base_url
    first_request = True

    while url:
        # If this is subsequent requests, don't need to pass params
        # will be provided in the skip URL
        if first_request:
            first_request = False
        else:
            params = None

        try:
            response = _fetch_page(
                url,
                headers={
                    "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                    "Content-Type": "application/json",
                },
                params=params,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Error, could not get instance data: {e.response.status_code} - {e.response.content}"
            )

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error, could not get instance data: {e}")

        data = response.json()

        for user in data["users"]:
            results.append(NintexUser(**user))

        url = data.get("nextLink")

    return results
