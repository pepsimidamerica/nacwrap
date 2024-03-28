"""
This module contains functions to interact with the Nintex Workflow Cloud API.
"""

import json
import os
from datetime import datetime
from typing import Optional

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
    If successful, returns rresponse which should be a dict containing
    instance ID that was created.
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set in environment")
    if start_data is None:
        start_data = {}
    try:
        response = requests.post(
            os.environ["NINTEX_BASE_URL"]
            + "/workflows/v1/designs/"
            + workflow_id
            + "/instances",
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            data=json.dumps({"startData": start_data}),
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
