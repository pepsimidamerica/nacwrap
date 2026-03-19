"""
This module contains functions relating to user management.
"""

import logging
import os

from nacwrap._auth import Decorators
from nacwrap._helpers import _get_ntx_headers, _get_paginated, _make_request
from nacwrap.data_model import NintexUser

logger = logging.getLogger(__name__)


@Decorators.refresh_token
def user_delete(id: str) -> None:
    """
    Delete a single Nintex User.

    :param id: Nintex User ID to delete.
    """
    url = os.environ["NINTEX_BASE_URL"] + f"/tenants/v1/users/{id}"

    _make_request(
        method="DELETE",
        url=url,
        headers=_get_ntx_headers(),
        context="delete user",
        success_status_codes=[204],
    )


@Decorators.refresh_token
def users_list(
    id: str | None = None,
    email: str | None = None,
    filter: str | None = None,
    role: str | None = None,
) -> list[dict]:
    """
    Get Nintex User Data.
    Returns: List of Dictionaries.

    :param ids: One or more user IDs to filter by
    :param email: User's email filter
    :param filter: User's name or email filter
    :param role: User's role filter
    """
    base_url = os.environ["NINTEX_BASE_URL"] + "/tenants/v1/users"

    params = {"id[]": id, "email[]": email, "filter": filter, "role[]": role}

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    results = _get_paginated(
        url=base_url,
        pagination_value="users",
        headers=_get_ntx_headers(),
        context="get users",
        params=params,
    )

    return results


def users_list_pd(
    id: str | None = None,
    email: str | None = None,
    filter: str | None = None,
    role: str | None = None,
) -> list[NintexUser]:
    """
    Get Nintex User Data.
    Returns: List of NintexUser pydantic objects.

    :param id: User's ID filter
    :param email: User's email filter
    :param filter: User's name or email filter
    :param role: User's role filter
    """
    usr_dict = users_list(id=id, email=email, filter=filter, role=role)

    return [NintexUser(**user) for user in usr_dict]
