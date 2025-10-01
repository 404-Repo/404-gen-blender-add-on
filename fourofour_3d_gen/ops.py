import bpy
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
        client = get_client()
        client.request_model(threegen.prompt)

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
)

register, unregister = bpy.utils.register_classes_factory(classes)

