import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

sys.path.insert(0, "")
from nacwrap import *


def test_task_search():
    task_dict = nacwrap.task_search(
        # workflow_name="Purchase Approval",
        status=TaskStatus.ACTIVE,
        assignee="robinsonhr@pepsimidamerica.com",
    )
    pprint(task_dict)

    tasks = nacwrap.task_search_pd(
        # workflow_name="Purchase Approval",
        status=TaskStatus.ACTIVE,
        assignee="robinsonhr@pepsimidamerica.com",
        dt_from=datetime.now() - timedelta(days=365),
        dt_to=datetime.now(),
    )
    pprint(tasks)

    for task in tasks:
        for a in task.taskAssignments:
            print(f"Workflow: {task.name}")
            print(f"  User: {a.assignee}")
            print(f"  Task ID: {task.id}")
            print(f"  Assignment ID: {a.id}\n")

            nacwrap.task_delegate(
                assignmentId=a.id,
                taskId=task.id,
                assignees=["clambert@pepsimidamerica.com"],
                message="This is a test!",
            )
            exit(0)


test_task_search()
