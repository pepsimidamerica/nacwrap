import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

sys.path.insert(0, "")
from nacwrap import *


def test_task_search():
    task_dict = nacwrap.task_search(workflow_name='Purchase Approval', status=TaskStatus.TERMINATED)
    pprint(task_dict)

    tasks = nacwrap.task_search_pd(workflow_name='Purchase Approval', status=TaskStatus.TERMINATED)
    pprint(tasks)

    for task in tasks:
        for a in task.taskAssignments:
            print(f'Workflow: {task.name}')
            print(f'  User: {a.assignee}')
            print(f'  Assignment ID: {a.id}\n')


test_task_search()
