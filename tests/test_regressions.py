"""
Regression tests for small bugs found in review.
"""

from unittest.mock import patch

from nacwrap.data_model import InstanceActions
from nacwrap.instances import instances_list_pd
from nacwrap.workflows import workflow_export


def test_workflow_export_url_has_slash() -> None:
    """
    workflow_export used to build ".../designs/<id>draft/export".
    """
    with patch("nacwrap.workflows._make_request") as mock_request:
        workflow_export("abc", "draft")
        workflow_export("abc", "published")

    urls = [c.kwargs["url"] for c in mock_request.call_args_list]
    assert urls[0].endswith("/designs/abc/draft/export")
    assert urls[1].endswith("/designs/abc/published/export")


def test_action_is_running_reads_status() -> None:
    """
    action_is_running used to raise AttributeError since Action had no status field.
    """
    action = {"id": "a", "name": "n", "label": "l", "type": "t"}
    instance = InstanceActions(
        instanceId="i",
        startDateTime="2026-01-01T00:00:00Z",
        status="Running",
        workflow={"id": "w", "name": "n", "version": "1", "eventType": "e"},
        actions=[
            {**action, "actionInstanceId": "done", "status": "Completed"},
            {**action, "actionInstanceId": "busy", "status": "Started"},
        ],
    )

    assert instance.action_is_running("done") is False
    assert instance.action_is_running("busy") is True


def test_instances_list_pd_accepts_str_status() -> None:
    """
    instances_list_pd used to call .value on a plain string status.
    """
    with patch("nacwrap.instances._get_paginated", return_value=[]) as mock_paginated:
        instances_list_pd(status="Running", instance_name="foo")

    params = mock_paginated.call_args.kwargs["params"]
    assert params["status"] == "running"
    assert params["name"] == "foo"
