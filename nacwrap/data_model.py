from enum import Enum
from datetime import date, datetime, timezone, timedelta
from typing import Literal, Optional, Union, List
from pydantic import BaseModel, Field


class TaskStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    COMPLETE = "complete"
    OVERRIDDEN = "overridden"
    TERMINATED = "terminated"
    ALL = "all"


class NintexTask(BaseModel):

    class TaskAssignment(BaseModel):

        class TaskURL(BaseModel):
            formUrl: str

        # TaskAssignment Attributes
        id: str
        status: str
        assignee: str
        createdDate: datetime
        completedBy: Optional[str] = Field(default=None)
        completedDate: Optional[datetime] = Field(default=None)
        outcome: Optional[str] = Field(default=None)
        completedById: Optional[str] = Field(default=None)
        updatedDate: datetime
        escalatedTo: Optional[str] = Field(default=None)
        urls: TaskURL

    # NintexTask Attributes
    assignmentBehavior: str
    completedDate: Optional[datetime] = Field(default=None)
    completionCriteria: str
    createdDate: datetime
    description: str
    dueDate: datetime
    id: str
    initiator: str
    isAuthenticated: bool
    message: str
    modified: datetime
    name: str
    outcomes: Optional[List[str]] = Field(default=None)
    status: TaskStatus
    subject: str
    taskAssignments: List[TaskAssignment]
    workflowId: str
    workflowInstanceId: str
    workflowName: str

    @property
    def age(self) -> timedelta:
        return datetime.now(timezone.utc) - self.createdDate


class NintexUser(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    isGuest: bool
    organizationId: str
    role: str

    @property
    def name(self):
        return self.firstName + " " + self.lastName
