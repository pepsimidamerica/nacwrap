import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from dotenv import load_dotenv

# Load env vars from a .env file
load_dotenv()

sys.path.insert(0, "")

from nacwrap import WorkflowStatus, instances_list_pd

res = instances_list_pd(workflow_name="Form 279", status=WorkflowStatus.RUNNING)

pass
