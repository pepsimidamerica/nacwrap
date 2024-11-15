import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

sys.path.insert(0, "")
from nacwrap import *


def test_list_instances():
    instances = nacwrap.instances_list(status=TaskStatus.PAUSED)
    pprint(instances)

    instances = nacwrap.instances_list_pd(status=TaskStatus.PAUSED)

    for i in instances:
        print(f'Name: {i.instanceName}')


def test_get_instance():
    instance_dict = nacwrap.instance_get(instanceId='d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4')
    pprint(instance_dict)

    instance = nacwrap.instance_get_pd(instanceId='d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4')
    print(instance)

# test_get_instance()
test_list_instances()
