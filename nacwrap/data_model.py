"""
Data model contains various enums and pydantic models used throughout the rest of the package.
"""

from datetime import datetime, timedelta, timezone
from enum import Enum, StrEnum

from pydantic import BaseModel, Field


class WorkflowStatus(StrEnum):
    """
    Represents the state of a given instance of a workflow.
    """

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"
    PAUSED = "paused"

    @classmethod
    def _missing_(cls, value: object) -> "WorkflowStatus | None":
        """
        If any value is not found, try to match case insensitively.
        Used when when converting string data.
        """
        value = str(value).lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None


class TaskStatus(StrEnum):
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
    def _missing_(cls, value: object) -> "TaskStatus | None":
        """
        If any value is not found, try to match case insensitively.
        Used when converting string data.
        """
        value = str(value).lower()
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
        parentId: str | None = Field(default=None)
        startDateTime: datetime | None = Field(default=None)
        endDateTime: datetime | None = Field(default=None)
        errorMessage: str | None = Field(default=None)
        logMessage: str | None = Field(default=None)

        @property
        def age(self) -> timedelta:
            """
            Returns the age of the action based on its start date.
            """
            if self.startDateTime:
                return datetime.now(timezone.utc) - self.startDateTime

            return timedelta(days=0)

    # NintexInstance attributes
    instanceId: str
    name: str | None = Field(default=None)
    startDateTime: datetime
    status: str
    errorMessage: str | None = Field(default=None)
    workflow: Workflow
    actions: list[Action]

    def action_is_running(self, action_instance_id: str) -> bool:
        """Looks for actions matching action_instance_id that are completed. Some actions are listed as completed
        by another entry in the Actions list of the instance, while the first instance of the action is still in a status of running.

        Args:
            actions (List[InstanceActions.Action]): List of workflow instance's actions.
            action_instance_id (str): Action ID to search for.

        Returns:
            bool: True if action was completed.
        """
        for action in self.actions:
            if (
                action.actionInstanceId == action_instance_id
                and action.status == "Completed"
            ):
                return False

        if action_instance_id not in [act.actionInstanceId for act in self.actions]:
            raise ValueError(
                "Action instance ID passed to action_is_running() does not exist in list of actions."
            )

        return True


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
    instanceName: str | None = Field(default=None)
    workflow: Workflow
    startDateTime: datetime
    endDateTime: datetime | None = Field(default=None)
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
        completedBy: str | None = Field(default=None)
        completedDate: datetime | None = Field(default=None)
        outcome: str | None = Field(default=None)
        completedById: str | None = Field(default=None)
        updatedDate: datetime
        escalatedTo: str | None = Field(default=None)
        urls: TaskURL | None = Field(default=None)

    # Task Attributes
    assignmentBehavior: str
    completedDate: datetime | None = Field(default=None)
    completionCriteria: str
    createdDate: datetime
    description: str
    dueDate: datetime | None = Field(default=None)
    id: str
    initiator: str
    isAuthenticated: bool
    message: str
    modified: datetime
    name: str
    outcomes: list[str] | None = Field(default=None)
    status: TaskStatus
    subject: str
    taskAssignments: list[TaskAssignment]
    workflowId: str
    workflowInstanceId: str
    workflowName: str

    @property
    def age(self) -> timedelta:
        """
        Returns the age of the task based on its created date.
        """
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
    def name(self) -> str:
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


class Connection(BaseModel):
    """
    Response model representing a connection in Nintex. Would be third-party
    connections or custom xtensions.
    """

    id: str
    display_name: str = Field(alias="displayName")
    is_invalid: bool = Field(alias="isInvalid")
    created_date: datetime = Field(alias="createdDate")
    contract_name: str = Field(alias="contractName")
    contract_id: str = Field(alias="contractId")
    created_by_user_id: str = Field(alias="createdByUserId")
    app_id: str = Field(alias="appId")
    contract_tags: str | None = Field(default=None, alias="contractTags")
    has_public_operation: bool | None = Field(alias="hasPublicOperation", default=None)
    private: bool = Field(alias="private")
    keep_alive: bool = Field(alias="keepAlive")
