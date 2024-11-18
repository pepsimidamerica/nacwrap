import os
from enum import Enum
from datetime import date, datetime
from typing import Literal, Optional, Union, List
import requests
from pprint import pprint
from pydantic import BaseModel, Field

from nacwrap._auth import Decorators
from nacwrap._helpers import _fetch_page, _put
from nacwrap.data_model import *

"""
This module contains functions relating to individual task assignments.
"""


def task_delegate(assignmentId: str, taskId: str, assignees: List[str], message: str):
    """
    Delegate a Nintex Task to another user.

    :param assignmentId: ID of task assignment to delegate.
    :param taskId: ID of task to delegate.
    :param assignees: List of user emails to delegate the task to.
    :param message: Message to include with delegation.
    """

    url = (
        os.environ["NINTEX_BASE_URL"]
        + f"/workflows/v2/tasks/{taskId}/assignments/{assignmentId}/delegate"
    )
    params = {"assignmentId": assignmentId, "taskId": taskId}
    data = {"assignees": assignees, "message": message}

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    try:
        response = _put(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            # params=params,
            data=data,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"HTTP Error when delegating task: {e.response.status_code} - {e.response.content}"
        )

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not delegate task: {e}")

    print(f"Response Status: {response.status_code}")


@Decorators.refresh_token
def task_search(
    workflow_name: str = None,
    instance_id: str = None,
    status: TaskStatus = None,
    assignee: str = None,
    dt_from: date = None,
    dt_to: date = None,
) -> List[dict]:
    """
    Get Nintex Task data.
    Returns: List of Dictionaries.

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

    results = []
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
        results += data["tasks"]
        url = data.get("nextLink")

    return results


def task_search_pd(
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
    task_dict = task_search(
        workflow_name=workflow_name,
        instance_id=instance_id,
        status=status,
        assignee=assignee,
        dt_from=dt_from,
        dt_to=dt_to,
    )
    results: List[NintexTask] = []
    for task in task_dict:
        results.append(NintexTask(**task))

    return results


# TODO Get a task

# TODO Complete a task
