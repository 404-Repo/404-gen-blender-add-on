import bpy
import base64
import json
import tempfile
import time
from .spz_loader import get_spz

from .protocol import Auth, PromptData, TaskStatus, TaskUpdate
from .gateway.gateway_api import GatewayApi
from .gateway.gateway_task import GatewayTask, GatewayTaskStatusResponse, GatewayTaskStatus


_GATEWAY_STATUS_CHECK_INTERVAL_SEC: int = 5
_GATEWAY_TASK_TIMEOUT_SEC: int = 10 * 60 # 10 minutes


class GatewayErrorBase(Exception):
    pass


class GatewayTimeoutError(GatewayErrorBase):
    pass


class GatewayFailureError(GatewayErrorBase):
    pass


class Client:

    def __init__(self) -> None:
        self._task: GatewayTask | None = None
        self._task_start_time: float | None = None
        gateway_url = bpy.context.preferences.addons[__package__].preferences.url
        gateway_api_key = bpy.context.preferences.addons[__package__].preferences.token
        self._gateway_api: GatewayApi = GatewayApi(gateway_url=gateway_url, gateway_api_key=gateway_api_key)

    @property
    def task_id(self) -> str | None:
        return self._task.id if self._task else None
    
    @property
    def prompt(self) -> str | None:
        return self._task.prompt if self._task else None

    def request_model(self, prompt: str) -> None:
        task = self._gateway_api.add_task(text_prompt=prompt)
        print(f"Task added: {task.id}")
        self._task = task
        self._task_start_time = time.time()
    
    def get_result(self) -> str | None:
        if self._task is None or self._task_start_time is None:
            return None
            
        # Check for timeout
        if time.time() - self._task_start_time > _GATEWAY_TASK_TIMEOUT_SEC:
            raise GatewayTimeoutError("Gateway timeout error")

        task_status_response = self._gateway_api.get_status(task=self._task)
        task_status = task_status_response.status

        if task_status not in [GatewayTaskStatus.SUCCESS, GatewayTaskStatus.FAILURE]:
            return None
        
        if task_status == GatewayTaskStatus.FAILURE:
            raise GatewayFailureError(f"Gateway failure error")

        if task_status == GatewayTaskStatus.SUCCESS:
            spz_data = self._gateway_api.get_result(task=self._task)
            print(f"Received result for task: {self._task.id}")

            loader = get_spz()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ply") as temp_file:
                ply_data = loader.decompress(spz_data, include_normals=False)
                temp_file.write(ply_data)
                filepath = temp_file.name
                print(f"Saved result to: {filepath}")
            return filepath

        return None
