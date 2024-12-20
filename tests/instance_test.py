import os
import sys
from datetime import datetime, timedelta
from pprint import pprint
from pydantic import BaseModel

sys.path.insert(0, "")
from nacwrap import *


class PurchDocStartData(InstanceStartData):
    requestor: str = Field(alias='se_txtrequestor')
    requestor_email: str = Field(alias="se_txtrequestoremail")
    purchaser_code: str = Field(alias='se_txtpurchasercode')


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


def test_get_instance():
    instance_dict = nacwrap.instance_get(
        instanceId="d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4"
    )
    pprint(instance_dict)

    instance = nacwrap.instance_get_pd(
        instanceId="d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4"
    )
    print(instance)


def test_instance_start_data():
    # sd = nacwrap.instance_start_data(instance_id='d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4')
    # pprint(sd)

    sd = nacwrap.instance_start_data_pd(
        instance_id="d39c4615-863d-47ff-a800-c4b82cdc1e1f_0_4",
        pydantic_model=PurchDocStartData,
    )
    pprint(sd)


# test_get_instance()
# test_list_instances()
test_instance_start_data()
