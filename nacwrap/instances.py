import json
import os
from datetime import datetime
from typing import Literal, Optional, Union

import requests

from nacwrap._auth import Decorators
from nacwrap._helpers import _fetch_page


@Decorators.refresh_token
def create_instance(workflow_id: str, start_data: Optional[dict] = None) -> dict:
    """
    Creates a Nintex workflow instance for a given workflow.
    If successful, returns response which should be a dict containing
    instance ID that was created.

    :param workflow_id: ID of the component workflow to create an instance for
    :param start_data: dictionary of start data, if the component workflow has any
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set in environment")
    if start_data is None:
        start_data = {}
    try:
        data = json.dumps({"startData": start_data})
        response = requests.post(
            os.environ["NINTEX_BASE_URL"]
            + "/workflows/v1/designs/"
            + workflow_id
            + "/instances",
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            data=data,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error creating instance for {start_data}: {e.response.status_code} - {e.response.content}"
        )
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error creating instance for {start_data}: {e}")

    return response.json()


@Decorators.refresh_token
def get_instance_data(
    workflow_name: Optional[str] = None,
    status: Optional[str] = None,
    order_by: Union[Literal["ASC", "DESC"], None] = None,
    from_datetime: Optional[datetime] = None,
    to_datetime: Optional[datetime] = None,
    page_size: Optional[int] = 100,
) -> list[dict]:
    """
    Get Nintex instance data Follows nextLink until no more pages.
    Function goes through all instance data in Nintex.

    Note: If from_datetime and to_datetime are not provided, the Nintex API
    defaults to returning the last 30 days. If you want everything, you need to
    explicitly use some sufficiently large time range.

    :param workflow_name: Name of the workflow to filter by
    :param status: Status of the workflow to filter by
    :param order_by: Order of the results
    :param from_datetime: Start date to filter by
    :param to_datetime: End date to filter by
    :param page_size: Number of results per page
    """
    base_url = os.environ["NINTEX_BASE_URL"] + "/workflows/v2/instances"
    params = {
        "workflowName": workflow_name,
        "status": status,
        "order": order_by,
        "from": (
            from_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if from_datetime else None
        ),
        "to": to_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if to_datetime else None,
        "pageSize": page_size,
    }

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
        results += data["instances"]
        url = data.get("nextLink")

    return results


# TODO Delete instance

# TODO Get instance start data
