"""
This module contains functions to interact with the Nintex Workflow Cloud API.
"""

import json
import os
from datetime import datetime
from typing import Literal, Optional, Union

import requests


class Decorators:
    """
    Decorators class
    """

    @staticmethod
    def refresh_token(decorated):
        """
        Decorator to refresh the access token if it has expired or generate
        a new one if it does not exist.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function
            Args:
                *args:
                **kwargs:

            Returns:
                decorated function
            """
            if "NTX_BEARER_TOKEN_EXPIRES_AT" not in os.environ:
                expires_at = "01/01/1901 00:00:00"
            else:
                expires_at = os.environ["NTX_BEARER_TOKEN_EXPIRES_AT"]
            if (
                "NTX_BEARER_TOKEN" not in os.environ
                or datetime.strptime(expires_at, "%m/%d/%Y %H:%M:%S") < datetime.now()
            ):
                Decorators.get_token()
            return decorated(*args, **kwargs)

        wrapper.__name__ = decorated.__name__
        return wrapper

    @staticmethod
    def get_token():
        """
        Get Nintex bearer token
        """
        if "NINTEX_BASE_URL" not in os.environ:
            raise Exception("NINTEX_BASE_URL not set in environment")
        if "NINTEX_CLIENT_ID" not in os.environ:
            raise Exception("NINTEX_CLIENT_ID not set in environment")
        if "NINTEX_CLIENT_SECRET" not in os.environ:
            raise Exception("NINTEX_CLIENT_SECRET not set in environment")
        if "NINTEX_GRANT_TYPE" not in os.environ:
            raise Exception("NINTEX_GRANT_TYPE not set in environment")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            os.environ["NINTEX_BASE_URL"] + "/authentication/v1/token",
            headers=headers,
            data={
                "client_id": os.environ["NINTEX_CLIENT_ID"],
                "client_secret": os.environ["NINTEX_CLIENT_SECRET"],
                "grant_type": os.environ["NINTEX_GRANT_TYPE"],
            },
            timeout=30,
        )
        try:
            os.environ["NTX_BEARER_TOKEN"] = response.json()["access_token"]
        except Exception as e:
            print("Error, could not set OS env bearer token: ", e)
            print(response.content)
            raise Exception("Error, could not set OS env bearer token: ", e)
        try:
            os.environ["NTX_EXPIRES_AT"] = response.json()["expires_at"]
        except Exception as e:
            print("Error, could not set os env expires at: ", e)
            raise Exception("Error, could not set os env expires at: ", e)


@Decorators.refresh_token
def create_instance(workflow_id: str, start_data: Optional[dict] = None) -> dict:
    """
    Creates a Nintex workflow instance for a given workflow.
    If successful, returns response which should be a dict containing
    instance ID that was created.
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set in environment")
    if start_data is None:
        print("No start data provided")
        start_data = {}
    try:
        data = json.dumps({"startData": start_data})
        print(data)
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
    except requests.exceptions.RequestException as e:
        print(f"Error creating instance for {start_data}: {e}")
        raise Exception(f"Error creating instance for {start_data}: {e}")
    if response.status_code != 202:
        print(f"Error creating instance for {start_data}")
        print(response.content)
        raise Exception(f"Error creating instance for {start_data}")

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

    - workflow_name: Name of the workflow to filter by
    - status: Status of the workflow to filter by
    - order_by: Order of the results
    - from_datetime: Start date to filter by
    - to_datetime: End date to filter by
    - page_size: Number of results per page

    Note: If from_datetime and to_datetime are not provided, the Nintex API
    defaults to returning the last 30 days. If you want everything, you need to
    explicitly use some sufficiently large time range.
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

        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            params=params,
            timeout=30,
        )
        pass
        if response.status_code == 200:
            data = response.json()
            results += data["instances"]
            url = data.get("nextLink")
        else:
            print("Error, could not get instance data: ", response.content)
            break
    return results


if __name__ == "__main__":
    # Example usage
    os.environ["NINTEX_BASE_URL"] = "https://us.nintex.io"
    os.environ["NINTEX_CLIENT_ID"] = ""
    os.environ["NINTEX_CLIENT_SECRET"] = ""
    os.environ["NINTEX_GRANT_TYPE"] = "client_credentials"

    results = get_instance_data(workflow_name="", order_by="DESC")
    pass
