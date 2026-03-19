"""
This module contains functions relating to individual tasks and assignments.
"""

import logging
import os
from datetime import date

from nacwrap._auth import Decorators
from nacwrap._helpers import (
    _get_ntx_headers,
    _get_paginated,
    _make_request,
)
from nacwrap.data_model import NintexTask, TaskStatus

logger = logging.getLogger(__name__)


@Decorators.refresh_token
def task_delegate(
    assignmentId: str, taskId: str, assignees: list[str], message: str = ""
) -> None:
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

    _make_request(
        method="PUT",
        url=url,
        headers=_get_ntx_headers(),
        context="task delegate",
        json={"assignees": assignees, "message": message},
    )


@Decorators.refresh_token
def task_search(
    workflow_name: str | None = None,
    instance_id: str | None = None,
    status: TaskStatus | None = None,
    assignee: str | None = None,
    dt_from: date | None = None,
    dt_to: date | None = None,
) -> list[dict]:
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

    results = _get_paginated(
        url=base_url,
        pagination_value="tasks",
        headers=_get_ntx_headers(),
        params=params,
        context="task search",
    )

    return results


def task_search_pd(
    workflow_name: str | None = None,
    instance_id: str | None = None,
    status: TaskStatus | None = None,
    assignee: str | None = None,
    dt_from: date | None = None,
    dt_to: date | None = None,
) -> list[NintexTask]:
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

    return [NintexTask(**task) for task in task_dict]


@Decorators.refresh_token
def task_get(task_id: str) -> dict:
    """
    Get the details of a specific task.

    :param task_id: The unique identifier for the task
    """
    url = os.environ["NINTEX_BASE_URL"] + f"/workflows/v2/tasks/{task_id}"

    response = _make_request(
        "GET",
        url=url,
        headers=_get_ntx_headers(),
        context="get task",
        success_status_codes=[200],
    )

    return response.json()


@Decorators.refresh_token
def task_complete(task_id: str, assignment_id: str, outcome: str) -> None:
    """
    Complete a task and specify an outcome.

    :param task_id: The unique identifier for the task
    :param assignment_id: The unique identifier for the task assignment
    :param outcome: Outcome of the task assignment, must match one of the tasks's defined outcomes
    """
    url = (
        os.environ["NINTEX_BASE_URL"]
        + f"/workflows/v2/tasks/{task_id}/assignments/{assignment_id}"
    )

    response = _make_request(
        "PATCH",
        url=url,
        headers=_get_ntx_headers(),
        context="complete task",
        json={"outcome": outcome},
        success_status_codes=[204],  # TODO Verify code once I get a task I can complete
    )

    logger.info(f"Response Status: {response.status_code}")
