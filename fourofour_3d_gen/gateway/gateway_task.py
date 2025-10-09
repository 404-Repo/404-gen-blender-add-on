from enum import Enum
from datetime import datetime

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
    reason: str | None = None


class GatewayTask(BaseModel):
    """Task for the gateway"""

    id: str
    result: bytes | None = None
    status: GatewayTaskStatus = GatewayTaskStatus.NO_RESULT
    reason: str | None = None
    prompt: str | None = None
    image: str | None = None
    start_time: datetime | None = None
    obj_type: str | None = None

