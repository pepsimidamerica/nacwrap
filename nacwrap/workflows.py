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

    :param limit: Maximum number of workflows to return. Defaults to 1000.
    :type limit: int, optional
    :return: list of workflows
    :rtype: list[dict]
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

    :param limit: Maximum number of workflows to return. Defaults to 1000.
    :type limit: int, optional
    :return: Pydantic data model of API response.
    :rtype: NintexWorkflows
    """
    workflows = workflows_list(limit=limit)
    return NintexWorkflows(workflows=workflows)


@Decorators.refresh_token
def workflow_permissions_list(workflow_id: str) -> dict:
    """
    Get the list of all workflow owners of a specific workflow design.

    :param workflow_id: The ID of the workflow design.
    :type workflow_id: str
    :return: Dictionary containing workflow owners.
    :rtype: dict
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

    :param workflow_id: The ID of the worklfow to update.
    :type workflow_id: str
    :param permissions: A list of permission dictionaries to update. Each entry should consist of an ID and a type (user or group).
    :type permissions: list[dict]
    :return: None
    :rtype: None
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
    Get the published version of a workflow design, including the start data.

    :param workflow_id: The ID of the worklfow to retrieve
    :type workflow_id: str
    :return: Dictionary containing the published workflow design.
    :rtype: dict
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

    :param workflow_id: The ID of the workflow to delete.
    :type workflow_id: str
    :param draft_only: If True, only delete the draft version of the workflow. Keep the published.
    :type draft_only: bool
    :return: None
    :rtype: None
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

    :param workflow_id: The ID of the workflow to pause.
    :type workflow_id: str
    :return: None
    :rtype: None
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

    :param workflow_id: The ID of the workflow to unpause.
    :type workflow_id: str
    :return: None
    :rtype: None
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

    :param workflow_id: The ID of the workflow to replace the tags of.
    :type workflow_id: str
    :param tags: A list of tags to set on the given worklfow. Each entry should be a dictionary containing the tag name (string) and optionally a color index (integer).
    :type tags: list[dict]
    :return: None
    :rtype: None
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

    :param workflow_id: The ID of the workflow to export.
    :type workflow_id: str
    :param workflow_type: Whether to export the published version of a workflow or a draft (if it currently has a draft copy).
    :type workflow_type: Literal["draft", "published"]
    :return: A dictionary containing the workflow key and the key's expiry date.
    :rtype: dict
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


@Decorators.refresh_token
def workflow_import(
    key: str,
    name: str,
    overwrite_existing: bool | None = None,
    workflow_dependency_config: dict | None = None,
    publish_when_configured: bool | None = None,
    assigned_use: Literal["Production", "Development"] | None = None,
    clear_var_defaults: bool | None = None,
) -> dict:
    """
    Import a workflow design into the tenant.

    :param key: The workflow key to be used for importing (received from the workflow_export endpoint).
    :type key: str
    :param name: The name to give to the imported workflow.
    :type name: str
    :param overwrite_existing: Set to true to import this workflow as a draft version of an existing workflow with the same name. If there is no workflow with the provided name in the tenant, the operation fails with an HTTP 400 error.
    :type overwrite_existing: bool, optional
    :param workflow_dependency_config: Workflow dependencies such as connections, tables, data lookups, configurable variables, component workflows, and start event configurations that you can remap to alternatives in the target tenant.
    :type workflow_dependency_config: dict, optional
    :param publish_when_configured: Set to true to automatically publish the workflow once it is fully configured. Otherwise will be imported as a draft.
    :type publish_when_configured: bool, optional
    :param assigned_use: Whether the workflow is intended for production of development use.
    :type assigned_use: Literal["Production", "Development"], optional
    :param clear_var_defaults: Set to true to import the workflow with no default values for configurable variables. By default, the imported workflow uses the default values defined in the exported workflow. If a workflowDependencyConfiguration is supplied, this parameter is ignored and the imported workflow uses the default values defined in the supplied workflowDependencyConfiguration.
    :type clear_var_defaults: bool, optional
    :return: Dictionary containing info about the imported workflow
    :rtype: dict
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/import"

    # Create JSON body from params
    data = {"key": key, "name": name}
    if overwrite_existing is not None:
        data["overwriteExisting"] = overwrite_existing
    if workflow_dependency_config:
        data["workflowDependencyConfiguration"] = workflow_dependency_config
    if publish_when_configured:
        data["publishWhenConfigured"] = publish_when_configured
    if assigned_use:
        data["assignedUse"] = assigned_use
    if clear_var_defaults is not None:
        data["clearVariableDefaultValues"] = clear_var_defaults

    # TODO Consider folding in packaged import into one func, rather than creating its own.

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=60,
            json=data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error importing worklfow: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when importing workflow: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not import worklfow: {e}")
        raise Exception(f"Error, could not import workflow: {e}") from e

    return response.json()


# TODO Import a packaged workflow


@Decorators.refresh_token
def workflow_dependencies_return(
    workflow_id: str, workflow_status: Literal["published", "draft"] | None = None
) -> dict:
    """
    Get a list of the connections, component workflows, tables, externally-configurable
    variables, and start event configurations that are used in a workflow.

    Use this with the Import a workflow operation to select alternate dependencies
    in the target tenant, or with the Publish a workflow operation to publish a
    new configuration of the workflow.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/dependencyConfig"

    params = None
    if workflow_status:
        params = {"workflowStatus": workflow_status}

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            params=params,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error getting workflow dependencies: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when getting workflow dependencies: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not get workflow dependencies: {e}")
        raise Exception(f"Error, could not get workflow dependencies: {e}") from e

    return response.json()


@Decorators.refresh_token
def workflow_publish_config(workflow_id: str, dependency_config: dict) -> dict:
    """
    Update a workflow's dependencies to change which connections,
    component workflows, tables, externally-configurable variables,
    or start event configurations the workflow uses, and publish the updated workflow.
    """
    url = f"{os.environ['NINTEX_BASE_URL']}/workflows/v1/designs/{workflow_id}/dependencyConfig"

    try:
        response = requests.put(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Accept": "application/json",
            },
            json=dependency_config,
            timeout=60,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP Error updating workflow dependencies: {e.response.status_code} - {e.response.content}"
        )
        raise Exception(
            f"HTTP Error when updating workflow dependencies: {e.response.status_code} - {e.response.content}"
        ) from e
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error, could not update workflow dependencies: {e}")
        raise Exception(f"Error, could not update workflow dependencies: {e}") from e

    return response.json()
