"""
Module contains functions for getting info about and interacting with
workflow instances.
"""

import json
import logging
import os
from datetime import datetime
from typing import Literal

import requests
from nacwrap._auth import Decorators
from nacwrap._helpers import (
    _basic_retry,
    _check_env,
    _fetch_page,
    _get_ntx_headers,
    _get_paginated,
    _make_request,
    _post,
)
from nacwrap.data_model import (
    InstanceActions,
    InstanceStartData,
    NintexInstance,
    ResolveType,
    WorkflowStatus,
)

logger = logging.getLogger(__name__)


@Decorators.refresh_token
def create_instance(workflow_id: str, start_data: dict | None = None) -> dict:
    """
    Creates a Nintex workflow instance for a given workflow.
    If successful, returns response which should be a dict containing
    instance ID that was created.

    :param workflow_id: ID of the component workflow to create an instance for
    :type workflow_id: str
    :param start_data: dictionary of start data, if the component workflow has any
    :type start_data: dict | None
    :return: response from the API, should be a dict containing instance ID
    :rtype: dict
    """
    _check_env("NINTEX_BASE_URL")

    url = (
        f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/instances"
    )

    response = _make_request(
        method="POST",
        url=url,
        headers=_get_ntx_headers(),
        context="creating instance",
        data=json.dumps({"startData": start_data or {}}),
    )

    return response.json()


@_basic_retry
@Decorators.refresh_token
def instance_get(instanceId: str) -> dict:
    """
    Calls Nintex's 'Get a Workflow Instance' API endpoint.
    Returns data as python dictionary.

    :param instanceId: Unique ID of workflow instance to return data for.
    :type instanceId: str
    :return: response from the API, should be a dict containing instance data
    :rtype: dict
    """
    base_url = os.environ["NINTEX_BASE_URL"] + f"/workflows/v2/instances/{instanceId}"

    response = _make_request(
        method="GET",
        url=base_url,
        headers=_get_ntx_headers(),
        context="getting instance",
        success_status_codes=[200],
    )

    return response.json()


def instance_get_pd(instanceId: str) -> InstanceActions:
    """
    Calls Nintex's 'Get a Workflow Instance' API endpoint.
    Returns data as a pydantic data model.

    :param instanceId: Unique ID of workflow instance to return data for.
    :type instanceId: str
    :return: pydantic data model containing instance data
    :rtype: InstanceActions
    """
    instance = instance_get(instanceId=instanceId)
    return InstanceActions(**instance)


@Decorators.refresh_token
def instances_list(
    workflow_name: str | None = None,
    instance_name: str | None = None,
    status: WorkflowStatus | None = None,
    order_by: Literal["ASC", "DESC"] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
    endDateTimeFrom: datetime | None = None,
    endDateTimeTo: datetime | None = None,
    page_size: int | None = 100,
) -> list[dict]:
    """
    Get Nintex instance data Follows nextLink until no more pages.
    Function goes through all instance data in Nintex.

    Note: If from_datetime and to_datetime are not provided, the Nintex API
    defaults to returning the last 30 days. If you want everything, you need to
    explicitly use some sufficiently large time range.

    :param workflow_name: Name of the workflow to filter by
    :param instance_name: Name of the instance to filter by
    :param status: Status of the workflow to filter by
    :param order_by: Order of the results
    :param from_datetime: Start date to filter by
    :param to_datetime: End date to filter by
    :param endDateTimeFrom: Begin date to filter intance end date.
    :param endDateTimeTo: End date to filter intance start end.
    :param page_size: Number of results per page
    """
    if status is not None:
        status = status.value

    base_url = os.environ["NINTEX_BASE_URL"] + "/workflows/v2/instances"
    params = {
        "workflowName": workflow_name,
        "name": instance_name,
        "status": status,
        "order": order_by,
        "from": (
            from_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if from_datetime else None
        ),
        "to": (
            to_datetime.strftime("%Y-%m-%dT23:59:59.0000000Z") if to_datetime else None
        ),
        "endDateTimeFrom": (
            endDateTimeFrom.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            if endDateTimeFrom
            else None
        ),
        "endDateTimeTo": (
            endDateTimeTo.strftime("%Y-%m-%dT23:59:59.0000000Z")
            if endDateTimeTo
            else None
        ),
        "pageSize": page_size,
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    response = _get_paginated(
        url=base_url,
        pagination_value="instances",
        headers=_get_ntx_headers(),
        params=params,
        context="instances list",
    )

    return response


@Decorators.refresh_token
def instances_list_pd(
    workflow_name: str | None = None,
    status: str | None = None,
    order_by: Literal["ASC", "DESC"] | None = None,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
    endDateTimeFrom: datetime | None = None,
    endDateTimeTo: datetime | None = None,
    page_size: int | None = 100,
) -> list[NintexInstance]:
    """
    Get Nintex instance data Follows nextLink until no more pages.
    Returns a list of NintexInstance pydantic objects.

    :param workflow_name: Name of the workflow to filter by.
    :param status: Status of the workflow to filter by.
    :param order_by: Order of the results.
    :param from_datetime: Begin date to filter intance start date.
    :param to_datetime: End date to filter intance start date.
    :param endDateTimeFrom: Begin date to filter intance end date.
    :param endDateTimeTo: End date to filter intance start end.
    :param page_size: Number of results per page
    """
    instance = instances_list(
        workflow_name=workflow_name,
        status=status,
        order_by=order_by,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        endDateTimeFrom=endDateTimeFrom,
        endDateTimeTo=endDateTimeTo,
        page_size=page_size,
    )
    result: list[NintexInstance] = []
    for i in instance:
        result.append(NintexInstance(**i))

    return result


@Decorators.refresh_token
def instance_resolve(instance_id: str, resolveType: ResolveType, message: str) -> None:
    """
    Resolves a paused workflow instance.

    :param instance_id: ID of instance to resolve.
    :param resolveType: Specify how to resolve the paused instance: "1" to retry the failed action, "2" to fail the instance.
    :param message: Message to display on the workflow instance page
    """
    url = (
        os.environ["NINTEX_BASE_URL"] + f"/workflows/v1/instances/{instance_id}/resolve"
    )

    _make_request(
        method="POST",
        url=url,
        headers=_get_ntx_headers(),
        context="resolving instance",
        success_status_codes=[202, 204],
        json={"resolveType": resolveType.value, "message": message},
    )


@Decorators.refresh_token
def instance_start_data(instance_id: str) -> dict:
    """
    Returns start data from a specific workflow instance.

    :param instance_id: ID of instance to return start data for.
    """
    url = (
        os.environ["NINTEX_BASE_URL"]
        + f"/workflows/v2/instances/{instance_id}/startdata"
    )

    response = _make_request(
        method="GET",
        url=url,
        headers=_get_ntx_headers(),
        context="getting instance start data",
        success_status_codes=[200],
    )

    return response.json()


def instance_start_data_pd(instance_id: str, pydantic_model: InstanceStartData):
    """
    Returns start data as a pydantic object for a specific workflow instance.

    :param instance_id: ID of instance to return start data for.
    :param pydantic_model: Pydantic model to populate with results returned from Nintex API.
    """
    sd = instance_start_data(instance_id=instance_id)
    return pydantic_model(**sd)


@Decorators.refresh_token
def instance_terminate(instance_id: str) -> None:
    """
    Terminates a specific workflow instance.

    :param instance_id: ID of workflow instance to terminate.
    """
    url = (
        os.environ["NINTEX_BASE_URL"]
        + f"/workflows/v1/instances/{instance_id}/terminate"
    )

    _make_request(
        method="POST",
        url=url,
        headers=_get_ntx_headers(),
        context="terminating instance",
        success_status_codes=[200],
    )
