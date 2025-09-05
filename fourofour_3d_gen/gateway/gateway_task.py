from enum import Enum

from pydantic import BaseModel


class GatewayTaskStatus(Enum):
    """Status of the task in gateway"""

    NO_RESULT = "NoResult"
    FAILURE = "Failure"
    PARTIAL_RESULT = "PartialResult"
    SUCCESS = "Success"


class GatewayTaskStatusResponse(BaseModel):
    """Response from the gateway for the task status"""

    status: GatewayTaskStatus
    """Status of the task in gateway"""
    reason: str | None = None
    """Reason for the status. If status is not SUCCESS, reason is not None."""


class GatewayTask(BaseModel):
    """Task for the gateway"""

    id: str
    """Unique id of the task in gateway"""
    prompt: str
    """Text prompt to generate the asset 3D asset"""
    # TODO: in what format should we store in bunny net.
    result: bytes | None = None
    """Result of the task in gateway in spz format"""
    task_status: GatewayTaskStatus = GatewayTaskStatus.NO_RESULT
    """Status of the task in gateway"""
