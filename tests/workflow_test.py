import os
import sys
from datetime import datetime, timedelta
from pprint import pprint
from pydantic import BaseModel

sys.path.insert(0, "")
from nacwrap import *


class PurchDocStartData(InstanceStartData):
    requestor: str = Field(alias="se_txtrequestor")
    requestor_email: str = Field(alias="se_txtrequestoremail")
    purchaser_code: str = Field(alias="se_txtpurchasercode")


def test_list_instances():
    instances = nacwrap.instances_list(
        workflow_name="Purchase Approval", status=WorkflowStatus.RUNNING
    )
    # pprint(instances)

    instances = nacwrap.instances_list_pd(
        workflow_name="Purchase Approval", status=WorkflowStatus.RUNNING
    )

    for i in instances:
        print(f"Name: {i.instanceName}")


def test_list_workflows():
    # workflows = nacwrap.workflows_list()

    # print(workflows)

    workflows = workflows_list_pd()

    print(workflows)


test_list_workflows()
