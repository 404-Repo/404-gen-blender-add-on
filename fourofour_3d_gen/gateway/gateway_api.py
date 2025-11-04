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

    

    def add_text_task(self, text_prompt: str) -> GatewayTask:
        """Adds a text task to the gateway."""
        try:
            url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.ADD_TASK)
            print(text_prompt)
            payload = {"prompt": text_prompt}
            headers = {"x-api-key": self._gateway_api_key, "x-client-origin": "blender" }
            response = self._http_client.post(url=url, json=payload, headers=headers)
            response.raise_for_status()
            return GatewayTask.model_validate_json(response.text)
        except Exception as e:
            raise GatewayAddTaskError(f"Gateway: error to add task: {e}") from e
        
    def add_image_task(self, image) -> GatewayTask:
        """Adds a image task to the gateway."""

        url = self._construct_url(host=self._gateway_url, route=GatewayRoutes.ADD_TASK)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name

        try:
            image.save_render(temp_path)
            with open(temp_path, "rb") as f:
                files = {"image": (os.path.basename(temp_path), f, "image/png")}
                headers = {"x-api-key": self._gateway_api_key, "x-client-origin": "blender" }
                response = self._http_client.post(url=url, files=files, headers=headers)
                response.raise_for_status()
                return GatewayTask.model_validate_json(response.text)
            
        except Exception as e:
            raise GatewayAddTaskError(f"Gateway: error to add task: {e}") from e
        
        finally:
                os.remove(temp_path)


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
        return f"{host}{route.value}?{urlencode(kwargs)}"

_gateway_instance = None

def get_addon_prefs() -> bpy.types.AddonPreferences:
    addon_name = "fourofour_3d_gen"  # top-level add-on folder name
    addon_entry = bpy.context.preferences.addons.get(addon_name)
    if addon_entry is None:
        raise RuntimeError(f"Add-on '{addon_name}' is not loaded")
    return addon_entry.preferences

def get_gateway():
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = GatewayApi("https://gateway-us-west.404.xyz:4443", "bf6714a5-10f4-42a7-9487-9620317e58cb")
    return _gateway_instance