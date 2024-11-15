import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

sys.path.insert(0, "")
from nacwrap import *


def test_task_resolve():
    pass


def test_task_search():
    task_dict = nacwrap.task_search(
        # workflow_name="Purchase Approval",
        status=TaskStatus.ACTIVE,
        assignee="clambert@pepsimidamerica.com",
    )
    pprint(task_dict)

    tasks = nacwrap.task_search_pd(
        # workflow_name="Purchase Approval",
        status=TaskStatus.ACTIVE,
        assignee="clambert@pepsimidamerica.com",
        dt_from=datetime.now() - timedelta(days=365),
        dt_to=datetime.now(),
    )
    pprint(tasks)

    for task in tasks:
        for a in task.taskAssignments:
            print(f"Workflow Name: {task.workflowName}")
            print(f"  Task Name: {task.name}")
            print(f"  User: {a.assignee}")
            print(f"  Task ID: {task.id}")
            print(f"  Assignment ID: {a.id}\n")

            if task.supports_multiple_users:
                # nacwrap.task_delegate(
                #     assignmentId=a.id,
                #     taskId=task.id,
                #     assignees=["jmaynor@pepsimidamerica.com"],
                #     message="This is a test!",
                # )
                exit(0)

            else:
                print(f"Skipping unsupported Assign a Task assignment.")


# test_task_search()
test_task_resolve()
