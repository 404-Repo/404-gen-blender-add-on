import bpy
from io import BytesIO
import os
import re
import time

from .gateway.gateway_api import get_gateway
from .gateway.gateway_task import GatewayTaskStatus
from .util.gaussian_splatting import import_gs
from .util.mesh_conversion import generate_mesh, generate_uvs, bake_texture
from .util.positioning import align_and_fit
from .spz_loader import get_spz

def on_image_change(self, context):
    if self.image_preview is None:
        self.image_preview = bpy.data.textures.new("Image Preview", type='IMAGE')
        self.image_preview.extension = 'CLIP'

    self.image_preview.image = self.image
    print("Updated Image Preview")

_job_manager_timer_registred: bool = False

def job_manager_timer_callback():
    global _job_manager_timer_registred
    job_manager = bpy.context.window_manager.threegen.job_manager
    if job_manager.has_jobs():
        try:
            job_manager.update()
        except Exception as e:
            print(e)
        return 2.0

    _job_manager_timer_registred = False
    return None

OBJECT_ENUM_ITEMS = [
    ('3DGS', "3DGS", "3DGS"),
    ('MESH', "Mesh", "Mesh"),   
]

class Job(bpy.types.PropertyGroup):
    id: bpy.props.StringProperty()
    crtime: bpy.props.FloatProperty()
    status: bpy.props.EnumProperty(
        name="Job Status",
        description="Defines which type of object to generate",
        items=[
            ('WAITING', "Waiting", "Waiting", 'PLAY', 0),
            ('RUNNING', "Running", "Running", 'SORTTIME', 1),
            ('FAILED', "Failed", "Failed", 'ERROR', 2),
            ('COMPLETED', "Completed", "Completed", 'CHECKMARK', 3)
        ],
        default='WAITING'
    )
    reason: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    prompt: bpy.props.StringProperty()
    image: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Image",
        description="A custom image property",
    )
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
    open: bpy.props.BoolProperty(default=False)

class JobManager(bpy.types.PropertyGroup):
    jobs: bpy.props.CollectionProperty(type=Job)

    def add_job(self):
        global _job_manager_timer_registred
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

        try:
            if threegen.replace_active_obj:
                job.replace_obj = bpy.context.object
                if threegen.include_placeholder_dims:
                    dims = job.replace_obj.dimensions
                    job.prompt = f"{job.prompt}, {int(dims.x*100)}cm wide, {int(dims.y*100)}cm deep and {int(dims.z*100)}cm high"
                
            if job.image:
                img_path = job.image.filepath_from_user()
                job.name,_ = os.path.splitext(os.path.basename(img_path))
                task = get_gateway().add_image_task(job.image)
            else:
                job.name = re.sub(r"\s+", "_", threegen.prompt)
                task = get_gateway().add_text_task(job.prompt)



            job.id = task.id

            if not _job_manager_timer_registred:
                bpy.app.timers.register(job_manager_timer_callback)
                _job_manager_timer_registred = True

            print(f"Job added: {job.id}")
        except Exception as e:
            job.status = 'FAILED'
            job.reason = str(e)            


    def remove_job(self, id):
        for i, job in enumerate(self.jobs):
            if job.id == id:
                self.jobs.remove(i)


    def update_job(self, job):
        try:
            if job.status == 'FAILED':
                return

            if time.time() - job.crtime > get_gateway().get_timeout():
                job.status = 'FAILED'
                job.reason = "connection timed out"
                return

            response = get_gateway().get_status(job.id)

            if response.status == GatewayTaskStatus.SUCCESS:
                spz_data = get_gateway().get_result(job.id)
                ply_data = BytesIO(get_spz().decompress(spz_data, include_normals=False))
                obj = import_gs(ply_data, job.name)

                if job.obj_type == 'MESH':
                    mesh_obj = generate_mesh(obj, job.voxel_size, job.adaptivity)
                    generate_uvs(mesh_obj, job.angle_limit, job.island_margin)
                    bake_texture(obj, mesh_obj, job.texture_size)
                    bpy.data.objects.remove(obj, do_unlink=True)
                    obj = mesh_obj

                if job.replace_obj:
                    align_and_fit(job.replace_obj, obj)
                    bpy.data.objects.remove(job.replace_obj, do_unlink=True)
                    job.replace_obj = None


                job.status = 'COMPLETED'
                self.remove_job(job.id)
        except Exception as e:
            job.status = 'FAILED'
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
    include_placeholder_dims: bpy.props.BoolProperty(default=False)
    job_manager: bpy.props.PointerProperty(
        type=JobManager,
        name="Job Manager",
        description="A job manager",
    )

classes = (Job, JobManager, WindowManagerProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.threegen = bpy.props.PointerProperty(type=WindowManagerProps)


def unregister():
    del bpy.types.WindowManager.threegen

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
