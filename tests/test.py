import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from nacwrap import (
    create_instance,
    instance_resolve,
    instance_terminate,
    instances_list,
    instances_list_pd,
)

res = instances_list(workflow_name="Sales Calls")

pass
