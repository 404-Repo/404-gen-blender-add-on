import bpy
import os
import requests
import tempfile
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

    GATEWAY_TASK_TIMEOUT_SEC: int = 10 * 60

    def __init__(self, gateway_url: str, gateway_api_key: str) -> None:
        self._http_client = requests.Session()
        self._gateway_url = gateway_url
        self._gateway_api_key = gateway_api_key

    def _format_add_task_error(self, error: Exception) -> str:
        if isinstance(error, requests.HTTPError):
            response = error.response
            if response is not None and response.status_code == 429:
                return "Gateway: too many requests. Please retry later."
        return f"Gateway: error to add task: {error}"

    def add_text_task(self, text_prompt: str, obj_type:str, seed:int) -> GatewayTask:
        """Adds a text task to the gateway."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.ADD_TASK)
            model = "404-3dgs" if obj_type == "3DGS" else "404-mesh"
            print(text_prompt)
            payload = {"prompt": text_prompt, "model": model, "seed": seed}
            headers = {"x-api-key": self._gateway_api_key, "x-client-origin": "blender" }
            response = self._http_client.post(url=url, json=payload, headers=headers)
            response.raise_for_status()
            return GatewayTask.model_validate_json(response.text)
        except Exception as e:
            raise GatewayAddTaskError(self._format_add_task_error(e)) from e
        
    def add_image_task(self, image, obj_type:str, seed:int) -> GatewayTask:
        """Adds a image task to the gateway."""

        url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.ADD_TASK)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name

        try:
            image.save_render(temp_path)
            with open(temp_path, "rb") as f:
                files = {"image": (os.path.basename(temp_path), f, "image/png")}
                model = "404-3dgs" if obj_type == "3DGS" else "404-mesh"
                headers = {"x-api-key": self._gateway_api_key, "x-client-origin": "blender" }
                response = self._http_client.post(
                    url=url,
                    files=files,
                    data={"model": model, "seed": seed},
                    headers=headers
                )
                response.raise_for_status()
                return GatewayTask.model_validate_json(response.text)
            
        except Exception as e:
            raise GatewayAddTaskError(self._format_add_task_error(e)) from e
        
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass


    def get_status(self, task_id:str) -> GatewayTaskStatusResponse:
        """Gets the status of a task."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.GET_STATUS, id=task_id)
            headers = {"x-api-key": self._gateway_api_key}
            response = self._http_client.get(url=url, headers=headers)
            response.raise_for_status()
            print(response.text)
            return GatewayTaskStatusResponse.model_validate_json(response.text)
        except Exception as e:
            raise GatewayGetStatusError(f"Gateway: error to get status: {e}") from e


    def get_result(self, task_id: str) -> bytes:
        """Gets generated 3D asset in spz format."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.GET_RESULT, id=task_id)
            headers = {"x-api-key": self._gateway_api_key}
            response = self._http_client.get(url=url, headers=headers)
            response.raise_for_status()
            if response.headers.get('content-disposition', '').startswith('attachment'):
                return cast(bytes, response.content)
            raise GatewayNoAttachmentError()
        except Exception as e:
            raise GatewayGetResultError(f"Gateway: error to get result: {e}") from e
        
    def get_timeout(self):
        return self.GATEWAY_TASK_TIMEOUT_SEC

    def _construct_url(self, *, host: str, route: GatewayRoutes, **kwargs: Any) -> str:
        query = urlencode(kwargs)
        if query:
            return f"{host}{route.value}?{query}"
        return f"{host}{route.value}"

_gateway_instance = None


def get_gateway():
    global _gateway_instance
    prefs = bpy.context.preferences.addons["bl_ext.user_default.fourofour_3d_gen"].preferences
    if (
        _gateway_instance is None
        or _gateway_instance._gateway_url != prefs.url
        or _gateway_instance._gateway_api_key != prefs.token
    ):
        _gateway_instance = GatewayApi(prefs.url, prefs.token)
    return _gateway_instance
