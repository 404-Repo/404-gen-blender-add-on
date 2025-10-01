import requests
from typing import Any, cast
from urllib.parse import urlencode

from .gateway_routes import GatewayRoutes
from .gateway_task import GatewayTask, GatewayTaskStatusResponse


class GatewayErrorBase(Exception):
    pass


class GatewayAddTaskError(GatewayErrorBase):
    pass


class GatewayGetStatusError(GatewayErrorBase):
    pass


class GatewayGetResultError(GatewayErrorBase):
    pass


class GatewayNoAttachmentError(GatewayErrorBase):
    pass


class GatewayApi:
    """API client for interacting with gateway."""

    def __init__(self, *, gateway_url: str, gateway_api_key: str) -> None:
        self._http_client = requests.Session()
        self._gateway_url = gateway_url
        self._gateway_api_key = gateway_api_key

    

    def add_task(self, text_prompt: str) -> GatewayTask:
        """Adds a task to the gateway."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.ADD_TASK)
            print(text_prompt)
            payload = {"prompt": text_prompt}
            headers = {"x-api-key": self._gateway_api_key}
            response = self._http_client.post(url=url, json=payload, headers=headers)
            response.raise_for_status()
            return GatewayTask.model_validate_json(response.text)
        except Exception as e:
            raise GatewayAddTaskError(f"Gateway: error to add task: {e}") from e

    def get_status(self, task: GatewayTask) -> GatewayTaskStatusResponse:
        """Gets the status of a task."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.GET_STATUS, id=task.id)
            headers = {"x-api-key": self._gateway_api_key}
            response = self._http_client.get(url=url, headers=headers)
            response.raise_for_status()
            print(response.text)
            return GatewayTaskStatusResponse.model_validate_json(response.text)
        except Exception as e:
            raise GatewayGetStatusError(f"Gateway: error to get status: {e}") from e

    def get_result(self, task: GatewayTask) -> bytes:
        """Gets generated 3D asset in spz format."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.GET_RESULT, id=task.id)
            headers = {"x-api-key": self._gateway_api_key}
            response = self._http_client.get(url=url, headers=headers)
            response.raise_for_status()
            if response.headers.get('content-disposition', '').startswith('attachment'):
                return cast(bytes, response.content)
            raise GatewayNoAttachmentError()
        except Exception as e:
            raise GatewayGetResultError(f"Gateway: error to get result: {e}") from e

    def _construct_url(self, *, host: str, route: GatewayRoutes, **kwargs: Any) -> str:
        return f"{host}{route.value}?{urlencode(kwargs)}"

