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
This module contains functions relating to individual task assignments.
"""


@Decorators.refresh_token
def task_search(
    workflow_name: str = None,
    instance_id: str = None,
    status: TaskStatus = None,
    assignee: str = None,
    dt_from: date = None,
    dt_to: date = None,
) -> List[NintexTask]:
    """
    Get Nintex Task data.
    Returns: List of NintexTask pydantic objects.

    Note: If from_datetime and to_datetime are not provided, the Nintex API
    defaults to returning the last 30 days. If you want everything, you need to
    explicitly use some sufficiently large time range.

    :param workflow_name: Name of the workflow to filter by
    :param instance_id:
    :param status: Status of the workflow to filter by
    :param assignee: Filter to tasks assigned to a specific user
    :param dt_from: Start date to filter by
    :param dt_to: End date to filter by
    """
    base_url = os.environ["NINTEX_BASE_URL"] + "/workflows/v2/tasks"
    params = {
        "workflowName": workflow_name,
        "workflowInstanceId": instance_id,
        "assignee": assignee,
        "from": (dt_from.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if dt_from else None),
        "to": dt_to.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if dt_to else None,
    }
    if status is not None:
        params["status"] = status.value

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    results: List[NintexTask] = []
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

        for task in data["tasks"]:

            if task["completedDate"] is not None:
                task["completedDate"] = datetime.strftime(
                    task["completedDate"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )

            results.append(NintexTask(**task))

        url = data.get("nextLink")

    return results


# TODO Get a task

# TODO Complete a task

# TODO Delgate a task assignment
