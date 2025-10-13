import bpy
from io import BytesIO
import os
import re
import time

from .gateway.gateway_api import gateway
from .gateway.gateway_task import GatewayTaskStatus
from .utils.gaussian_splatting import import_gs
from .utils.mesh_conversion import generate_mesh, generate_uvs, bake_texture
from .spz_loader import get_spz

def on_image_change(self, context):
    if self.image_preview is None:
        self.image_preview = bpy.data.textures.new("Image Preview", type='IMAGE')
        self.image_preview.extension = 'CLIP'

    self.image_preview.image = self.image
    print("Updated Image Preview")

def job_manager_timer_callback():
    job_manager = bpy.context.window_manager.threegen.job_manager
    if job_manager.has_jobs():
        try:
            job_manager.update()
        except Exception as e:
            print(e)
        return 1.0

    job_manager.timer_registered = False
    return None

OBJECT_ENUM_ITEMS = [
    ('3DGS', "3DGS", "3DGS", 'OUTLINER_DATA_POINTCLOUD'),
    ('MESH', "Mesh", "Mesh", 'MESH_DATA'),   
]

class Job(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    crtime: bpy.props.FloatProperty()
    status: bpy.props.EnumProperty(
        name="Job Status",
        description="Defines which type of object to generate",
        items=[
            ('RUNNING', "Running", "Running", 'SORTTIME'),
            ('FAILED', "Failed", "Failed", 'ERROR'),
            ('COMPLETED', "Completed", "Completed", 'CHECKMARK')
        ]
    )
    name: bpy.props.StringProperty()
    prompt: bpy.props.StringProperty()
    image: bpy.props.StringProperty()
    angle_limit: bpy.props.FloatProperty(default=1.0, precision=3)
    island_margin: bpy.props.FloatProperty(default=0.0, precision=3)
    texture_size: bpy.props.IntProperty(default=4096)
    voxel_size: bpy.props.FloatProperty(default=0.01, precision=3)
    adaptivity: bpy.props.FloatProperty(default=0.0, precision=3)
    obj_type: bpy.props.EnumProperty(
        name="Object type",
        description="Defines which type of object to generate",
        items=OBJECT_ENUM_ITEMS
    )
    replace_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="The object to be replaced",
        description="A custom image property",
    )

class JobManager(bpy.types.PropertyGroup):
    jobs: bpy.props.CollectionProperty(type=Job)
    timer_registered: bpy.props.BoolProperty(default=False)

    def add_job(self):
        threegen = bpy.context.window_manager.threegen
        job = self.jobs.add()
        job.crtime = time.time()
        job.status = 'RUNNING'
        job.prompt = threegen.prompt
        job.image = threegen.image
        job.angle_limit = threegen.angle_limit
        job.island_margin = threegen.island_margin
        job.texture_size = threegen.texture_size
        job.voxel_size = threegen.voxel_size
        job.adaptivity = threegen.adaptivity
        job.obj_type = threegen.obj_type

        if threegen.replace_active_object:
            job.replace_obj = bpy.context.object
        
        if job.image:
            img_path = job.image.filepath_from_user()
            job.name = os.path.splitext(os.path.basename(img_path))
            task = gateway().add_image_task(job.image)
        else:
            job.name = re.sub(r"\s+", "_", job.prompt)
            task = gateway().add_text_task(job.prompt)

        job.id = task.id

        if not self.timer_registered:
            bpy.app.timers.register(job_manager_timer_callback)
            self.timer_registered = True
        print(f"Job added: {job.id}")


    def remove_job(self, id):
        for i, job in enumerate(self.jobs):
            if job.id == id:
                self.jobs.remove(i)


    def update_job(self, job):
        try:
            if job.status == 'FAILURE':
                return

            if time.time() - job.crtime > gateway().get_timeout():
                job.status = 'FAILURE'
                job.reason = "connection timed out"
                return

            status, reason = gateway().get_status(job.id)

            if status == GatewayTaskStatus.SUCCESS:
                spz_data = gateway().get_result(job.id)
                ply_data = BytesIO(get_spz().decompress(spz_data, include_normals=False))
                gs_obj = import_gs(ply_data, job.name)

                if job.obj_type == 'MESH':
                    mesh_obj = generate_mesh(gs_obj, job.voxel_size, job.adaptivity)
                    generate_uvs(mesh_obj, job.angle_limit, job.island_margin)
                    bake_texture(gs_obj, mesh_obj, job.texture_size)
                    bpy.data.objects.remove(gs_obj, do_unlink=True)

                if job.replace_obj:
                    # fit and transform
                    ...

                job.status = 'SUCCESS'
                self.remove_job(job.id)
        except Exception as e:
            job.status = 'FAILURE'
            job.reason = str(e)

    def update(self):
        for job in self.jobs:
            self.update_job(job)

    def has_jobs(self):
        return len(self.jobs) > 0

class WindowManagerProps(bpy.types.PropertyGroup):
    prompt: bpy.props.StringProperty()
    image: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Image",
        description="A custom image property",
        update=on_image_change
    )
    image_preview: bpy.props.PointerProperty(
        name="Texture",
        type=bpy.types.Texture,
        description="Linked texture for preview"
    )
    keep_original: bpy.props.BoolProperty(default=False)
    angle_limit: bpy.props.FloatProperty(default=1.0, precision=3)
    island_margin: bpy.props.FloatProperty(default=0.0, precision=3)
    texture_size: bpy.props.IntProperty(default=4096)
    voxel_size: bpy.props.FloatProperty(default=0.01, precision=3)
    adaptivity: bpy.props.FloatProperty(default=0.0, precision=3)
    obj_type: bpy.props.EnumProperty(
        name="Object type",
        description="Defines which type of object to generate",
        items=OBJECT_ENUM_ITEMS,
        default='3DGS'
    )
    replace_active_obj: bpy.props.BoolProperty(default=False)
    jobs: bpy.props.CollectionProperty(type=JobProps)


classes = (Job, JobManager, WindowManagerProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.threegen = bpy.props.PointerProperty(type=WindowManagerProps)


def unregister():
    del bpy.types.WindowManager.threegen

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
