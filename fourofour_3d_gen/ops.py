import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Context, Operator
from bpy.props import StringProperty

from .client import get_client
from .data_collection import track
from .mesh_conversion import generate_mesh, generate_uvs, bake_texture

class GenerateOperator(Operator):
    """Generate 3DGS model"""

    bl_idname = "threegen.generate"
    bl_label = "Generate"

    def execute(self, context:Context):
        threegen = context.window_manager.threegen
 
        if not threegen.image and not threegen.prompt:
            return {"CANCELLED"}

        threegen.job_manager.add_job()
        return {"FINISHED"}
        

    
class RemoveTaskOperator(Operator):
    """Remove a task from the list"""

    bl_idname = "threegen.remove_task"
    bl_label = "Remove"

    task_id: StringProperty()

    def execute(self, context:Context):
        client = get_client()
        client.remove_task(self.task_id)
        print(f"deleting {self.task_id}")
        return {"FINISHED"}
    
class OpenImageOperator(Operator, ImportHelper):
    """Open an Image File"""
    bl_idname = "image.open_file"
    bl_label = "Open Image File"

    # File filter for images
    filter_glob: StringProperty(
        default="*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tga;*.exr",
        options={'HIDDEN'},
    )

    def execute(self, context):
        max_size = 1024
        threegen = context.window_manager.threegen
        image_path = self.filepath
        try:
            # Load the image into bpy.data.images
            img = bpy.data.images.load(image_path, check_existing=True)
            threegen.image = img

            width, height = img.size
            if width >= height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))

            if (new_width, new_height) != (width, height):
                img.scale(new_width, new_height)


            self.report({'INFO'}, f"Loaded image: {img.name}")
        except RuntimeError:
            self.report({'ERROR'}, "Could not load image. Check the file path.")
        return {'FINISHED'}
  
class MeshConversionOperator(Operator):
    """Create Mesh from 3DGS model"""

    bl_idname = "threegen.generate_mesh"
    bl_label = "Generate Mesh"

    def execute(self, context):
        threegen = context.window_manager.threegen
        gs_obj = context.active_object
        keep_original = threegen.keep_original
        voxel_size = threegen.voxel_size
        adaptivity = threegen.adaptivity
        texture_size = threegen.texture_size
        angle_limit = threegen.angle_limit
        island_margin = threegen.island_margin

        mesh_obj = generate_mesh(gs_obj, voxel_size, adaptivity)
        generate_uvs(mesh_obj, angle_limit, island_margin)
        bake_texture(gs_obj, mesh_obj, texture_size)

        if keep_original:
            mesh_obj.location.x += mesh_obj.dimensions.x
        else:
            bpy.data.objects.remove(gs_obj, do_unlink=True)

        return {'FINISHED'}


classes = (
    GenerateOperator,
    MeshConversionOperator,
    RemoveTaskOperator,
    OpenImageOperator,
)

register, unregister = bpy.utils.register_classes_factory(classes)

