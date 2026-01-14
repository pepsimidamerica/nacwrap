"""
Data model contains various enums and pydantic models used throughout the rest of the package.
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """
    Represents the state of a given instance of a workflow.
    """

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"

    @classmethod
    def _missing_(cls, value):
        """
        If any value is not found, try to match case insensitively. Used when when converting string data.
        """
        value = value.lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None


class TaskStatus(str, Enum):
    """
    Represents the state of a given task assignment.
    """

    ACTIVE = "active"
    ESCALATED = "active-escalated"
    EXPIRED = "expired"
    COMPLETE = "complete"
    OVERRIDDEN = "overridden"
    TERMINATED = "terminated"
    PAUSED = "paused"
    ALL = "all"

    @classmethod
    def _missing_(cls, value):
        """
        If any value is not found, try to match case insensitively. Used when converting string data.
        """
        value = value.lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None


class ResolveType(Enum):
    """
    When a worklfow instance fails, the instance can be resolved either through
    retrying the action that caused the failure. Or fully setting the instance to failed.
    """

    RETRY = "1"
    FAIL = "2"


class InstanceActions(BaseModel):
    """
    Response Data Model for 'Get a Workflow Instance' API Endpoint.
    """

    class Workflow(BaseModel):
        id: str
        name: str
        version: str
        eventType: str

    class Action(BaseModel):
        id: str
        actionInstanceId: str
        name: str
        label: str
        type: str
        parentId: Optional[str] = Field(default=None)
        startDateTime: Optional[datetime] = Field(default=None)
        endDateTime: Optional[datetime] = Field(default=None)
        errorMessage: Optional[str] = Field(default=None)
        logMessage: Optional[str] = Field(default=None)

        @property
        def age(self) -> timedelta:
            if self.startDateTime:
                return datetime.now(timezone.utc) - self.startDateTime
            else:
                return timedelta(days=0)

    # NintexInstance attributes
    instanceId: str
    name: Optional[str] = Field(default=None)
    startDateTime: datetime
    status: str
    errorMessage: Optional[str] = Field(default=None)
    workflow: Workflow
    actions: list[Action]


class NintexInstance(BaseModel):
    """
    Represents a particular instance of a workflow. Includes core info of the workflow,
    when it was started, who by, and its status.
    """

    class StartEvent(BaseModel):
        eventType: str  # Optional[str] = Field(default=None)

    class Workflow(BaseModel):
        id: str
        name: str
        version: str

    instanceId: str
    instanceName: Optional[str] = Field(default=None)
    workflow: Workflow
    startDateTime: datetime
    endDateTime: Optional[datetime] = Field(default=None)
    status: WorkflowStatus
    startEvent: StartEvent


class NintexTask(BaseModel):
    """
    Response Data Model for Nintex Tasks from API Endpoints.
    """

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
        urls: Optional[TaskURL] = Field(default=None)

    # Task Attributes
    assignmentBehavior: str
    completedDate: Optional[datetime] = Field(default=None)
    completionCriteria: str
    createdDate: datetime
    description: str
    dueDate: Optional[datetime] = Field(default=None)
    id: str
    initiator: str
    isAuthenticated: bool
    message: str
    modified: datetime
    name: str
    outcomes: Optional[list[str]] = Field(default=None)
    status: TaskStatus
    subject: str
    taskAssignments: list[TaskAssignment]
    workflowId: str
    workflowInstanceId: str
    workflowName: str

    @property
    def age(self) -> timedelta:
        return datetime.now(timezone.utc) - self.createdDate

    @property
    def supports_multiple_users(self) -> bool:
        """
        Returns true if task was created by the assign a task to multiple users action.
        """
        return self.taskAssignments[0].urls is not None


class NintexUser(BaseModel):
    """
    Response Data Model for Nintex Users from API Endpoints.
    """

    id: str
    email: str
    firstName: str
    lastName: str
    isGuest: bool
    organizationId: str
    role: str

    @property
    def name(self):
        """
        Returns full name of user.
        """
        return self.firstName + " " + self.lastName


class NintexWorkflows(BaseModel):
    """
    Response Data Model for Nintex Workflows API Endpoints.
    """

    class Workflow(BaseModel):
        id: str
        name: str
        lastModified: datetime

    # NintexWorkflows Attributes
    workflows: list[Workflow]


class InstanceStartData(BaseModel):
    """
    Generic start data for an instance. Varies workflow-to-workflow.
    """

    pass
