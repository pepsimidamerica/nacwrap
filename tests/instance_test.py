import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

sys.path.insert(0, "")
from nacwrap import *


def test_get_instance():
    instance_dict = nacwrap.get_instance(instanceId='d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4')
    pprint(instance_dict)

    instance = nacwrap.get_instance_pd(instanceId='d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4')
    print(instance)

test_get_instance()
