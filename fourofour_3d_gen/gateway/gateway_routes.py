from enum import Enum


class GatewayRoutes(Enum):
    """Routes for gateway nodes"""

    ADD_TASK = "/add_task"
    """Send text prompt to gateway to generate 3D asset."""
    GET_STATUS = "/get_status"
    """Get status of the task."""
    GET_RESULT = "/get_result"
    """Get result of the generation in spz format."""
