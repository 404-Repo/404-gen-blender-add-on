import bpy
import re
from io import BytesIO
import tempfile
from datetime import datetime
from .spz_loader import get_spz
from .gateway.gateway_api import GatewayApi
from .gateway.gateway_task import GatewayTask, GatewayTaskStatus
from .gaussian_splatting import import_gs
from .mesh_conversion import generate_mesh, generate_uvs, bake_texture

_GATEWAY_STATUS_CHECK_INTERVAL_SEC: int = 5
_GATEWAY_TASK_TIMEOUT_SEC: int = 10 * 60 # 10 minutes

class Client:

    def __init__(self) -> None:
        gateway_url = bpy.context.preferences.addons[__package__].preferences.url
        gateway_api_key = bpy.context.preferences.addons[__package__].preferences.token
        self._gateway_api: GatewayApi = GatewayApi(gateway_url=gateway_url, gateway_api_key=gateway_api_key)
        self._tasks: list[GatewayTask] = []
        self.timer_registered: bool = False

    def request_model(self, prompt: str) -> None:
        threegen = bpy.context.window_manager.threegen
        task = self._gateway_api.add_task(prompt)
        task.start_time = datetime.now()
        task.prompt = prompt
        task.obj_type = threegen.obj_type
        self._tasks.append(task)

        if not self.timer_registered:
            bpy.app.timers.register(client_timer_callback)
            self.timer_registered = True
        print(f"Task added: {task.id}")
    
    def update_tasks(self):
        for task in self._tasks:

            # Check for timeout
            if (datetime.now() - task.start_time).total_seconds() > _GATEWAY_TASK_TIMEOUT_SEC:
                task.status = GatewayTaskStatus.FAILURE
                task.reason = "Connection timed out"
                continue

            if task.status in [GatewayTaskStatus.FAILURE, GatewayTaskStatus.SUCCESS]:
                continue

            # Update status
            task_status_response = self._gateway_api.get_status(task)
            task.status = task_status_response.status
            task.reason = task_status_response.reason

            if task.status == GatewayTaskStatus.SUCCESS:
                spz_data = self._gateway_api.get_result(task)
                loader = get_spz()
                ply_data = BytesIO(loader.decompress(spz_data, include_normals=False))
                name = re.sub(r"\s+", "_", task.prompt)
                gs_obj = import_gs(ply_data, name)

                if task.obj_type == 'MESH':
                    threegen = bpy.context.window_manager.threegen
                    voxel_size = threegen.voxel_size
                    adaptivity = threegen.adaptivity
                    texture_size = threegen.texture_size
                    angle_limit = threegen.angle_limit
                    island_margin = threegen.island_margin
                    mesh_obj = generate_mesh(gs_obj, voxel_size, adaptivity)
                    generate_uvs(mesh_obj, angle_limit, island_margin)
                    bake_texture(gs_obj, mesh_obj, texture_size)
                    bpy.data.objects.remove(gs_obj, do_unlink=True)

                self._tasks.remove(task)
                print(f"Received result for task: {task.id}")

    def remove_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                self._tasks.remove(task)

    def has_tasks(self):
        return len(self._tasks) > 0

_client_instance = None

def get_client():
    global _client_instance
    if _client_instance is None:
        _client_instance = Client()
    return _client_instance

def client_timer_callback():
    client = get_client()
    if client._tasks:
        try:
            client.update_tasks()
        except Exception as e:
            print(e)
        return 1.0

    client.timer_registered = False
    return None