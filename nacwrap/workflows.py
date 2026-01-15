"""
This module contains functions to interact with workflows.
"""

import logging
import os
from typing import Literal

import requests
from nacwrap._auth import Decorators
from nacwrap._helpers import _fetch_page
from nacwrap.data_model import NintexWorkflows
from nacwrap.exceptions import WorkflowApiError

logger = logging.getLogger(__name__)


@Decorators.refresh_token
def workflows_list(limit: int = 1000) -> list[dict]:
    """
    Get Nintex Workflow information.

    Args:
        limit (int, optional): Max number of workflows to return. Defaults to 1000.

    Raises:
        WorkflowApiError: Generic error when API call fails.

    Returns:
        list[dict]: _description_
    """
    base_url = (
        os.environ["NINTEX_BASE_URL"] + f"/workflows/v1/designs/published?limit={limit}"
    )
    results = []
    url = base_url

    while url:
        try:
            response = _fetch_page(
                url,
                headers={
                    "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error, could not get workflow data: {e.response.status_code} - {e.response.content}"
            )
            raise WorkflowApiError(
                f"Error, could not get workflow data: {e.response.status_code} - {e.response.content}"
            ) from e
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error, could not get workflow data: {e}")
            raise WorkflowApiError(f"Error, could not get workflow data: {e}") from e

        data = response.json()
        results += data["workflows"]
        url = data.get("nextLink")

    return results


def workflows_list_pd(limit: int = 1000) -> NintexWorkflows:
    """
    Get Nintex Workflow information.
    Returns data as a pydantic data model.

    Returns:
        NintexWorkflows: Pydantic data model of API response.
    """
    workflows = workflows_list(limit=limit)
    return NintexWorkflows(workflows=workflows)


@Decorators.refresh_token
def workflow_permissions_list(workflow_id: str) -> dict:
    """
    Get the list of all workflow owners of a specific workflow design.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/permissions"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when getting permissions: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when getting permissions: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get permissions: {e}")
        raise Exception(f"Error, could not get permissions: {e}") from e

    return response.json()


@Decorators.refresh_token
def workflow_permissions_update(workflow_id: str, permissions: list[dict]) -> None:
    """
    Update the workflow owners of a specific workflow design.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/permissions"

    try:
        response = requests.put(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            json={"permissions": permissions},
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when updating permissions: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when updating permissions: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not update permissions: {e}")
        raise Exception(f"Error, could not update permissions: {e}") from e


@Decorators.refresh_token
def workflow_design_return(workflow_id: str) -> dict:
    """
    Get the published version of a workflow designm including the start data.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}"

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when getting workflow design: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when getting workflow design: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get worklfow design: {e}")
        raise Exception(f"Error, could not get workflow design: {e}") from e

    return response.json()


@Decorators.refresh_token
def workflow_delete(workflow_id: str, draft_only: bool = False) -> None:
    """
    Delete a workflow design. This does not impact any running instances of the workflow.
    By default, will delete both the published and any draft versions of the workflow.

    :param draft_only: If True, only delete the draft version of the workflow. Keep the published.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}"

    if draft_only:
        url += "/draft"

    try:
        response = requests.delete(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when deleting workflow: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when deleting workflow: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not delete workflow: {e}")
        raise Exception(f"Error, could not delete workflow: {e}") from e


@Decorators.refresh_token
def workflow_pause(workflow_id: str) -> None:
    """
    Prevent a published workflow from being run. Until this workflow is unpaused,
    instances of the workflow cannot be created. Pausing a workflow does not terminate
    any running instances.
    """
    url = (
        f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/deactivate"
    )

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when pausing workflow: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when pausing workflow: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not pause workflow: {e}")
        raise Exception(f"Error, could not pause workflow: {e}") from e


@Decorators.refresh_token
def workflow_unpause(workflow_id: str) -> None:
    """
    Unpause a published workflow so that instances of this workflow can be created.
    Unpausing a workflow does not create or start an instance.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/activate"

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when unpausing workflow: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when unpausing workflow: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not unpause workflow: {e}")
        raise Exception(f"Error, could not unpause workflow: {e}") from e


@Decorators.refresh_token
def workflow_add_tags(workflow_id: str, tags: list[dict]) -> None:
    """
    Add tags to a workflow design to add categories or metadata.
    A workflow can have a maximum of ten tags. By default, designers and developers
    can only add existing tags to workflows. To allow designers and developers to
    create new tags, enable Allow workflow designers and developers to create tags
    in the tenant Tag settings.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/tags"

    try:
        response = requests.put(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=60,
            json={"tags": tags},
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error when adding tags: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when adding tags: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not add tags: {e}")
        raise Exception(f"Error, could not add tags: {e}") from e


@Decorators.refresh_token
def workflow_export(
    workflow_id: str,
    workflow_type: Literal["draft", "published"],
) -> dict:
    """
    Export a draft or published workflow design to import it into another tenant.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}"

    if workflow_type == "draft":
        url += "draft/export"
    if workflow_type == "published":
        url += "published/export"

    # TODO Consider just adding in the export package worklfow function
    # instead of making it its own thing below. The general purpose is the same. The only
    # difference is what URl you hit and what formatting your request takes.
    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error exporting worklfow: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when exporting workflow: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not export worklfow: {e}")
        raise Exception(f"Error, could not export workflow: {e}") from e

    return response.json()


# TODO Export packaged draft/published worfklow

# TODO Import a workflow

# TODO Import a packaged workflow

# TODO Get workflow dependencies

# TODO Publish a workflow configuration
