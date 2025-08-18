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


def request_model(prompt: str) -> str | None:
    gateway_url = bpy.context.preferences.addons[__package__].preferences.url
    gateway_api_key = bpy.context.preferences.addons[__package__].preferences.token
    filepath = None

    gateway_api = GatewayApi(gateway_url=gateway_url, gateway_api_key=gateway_api_key)

    task = gateway_api.add_task(text_prompt=prompt)
    print(f"Task added: {task.id}")

    task_status = GatewayTaskStatus.NO_RESULT
    start_time = time.time()
    while task_status not in [GatewayTaskStatus.SUCCESS, GatewayTaskStatus.FAILURE]:
        if time.time() - start_time > _GATEWAY_TASK_TIMEOUT_SEC:
            raise GatewayTimeoutError("Gateway timeout error")
        time.sleep(_GATEWAY_STATUS_CHECK_INTERVAL_SEC)
        task_status = gateway_api.get_status(task=task).status
        print(f"Task status: {task_status}")

    if task_status == GatewayTaskStatus.FAILURE:
        raise GatewayFailureError("Gateway failure error")

    if task_status == GatewayTaskStatus.SUCCESS:
        spz_data = gateway_api.get_result(task=task)
        print(f"Received result for task: {task.id}")

        loader = get_spz()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ply") as temp_file:
            ply_data = loader.decompress(spz_data, include_normals=False)
            temp_file.write(ply_data)
            filepath = temp_file.name
            print(f"Saved result to: {filepath}")

    return filepath
