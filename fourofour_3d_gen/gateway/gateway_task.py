from enum import Enum
from datetime import datetime
import re

from pydantic import BaseModel, field_validator
import bpy
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

    @field_validator("status", mode="before")
    @classmethod
    def _normalize_partial_result(cls, value):
        if isinstance(value, str):
            if value == GatewayTaskStatus.PARTIAL_RESULT.value:
                return value
            if re.fullmatch(r"PartialResult\(\d+\)", value):
                return GatewayTaskStatus.PARTIAL_RESULT.value
        return value


class GatewayTask(BaseModel):
    """Task for the gateway"""

    id: str
    result: bytes | None = None
    status: GatewayTaskStatus = GatewayTaskStatus.NO_RESULT
    reason: str | None = None

