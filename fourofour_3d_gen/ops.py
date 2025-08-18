import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Context, Operator, Event
from bpy.props import StringProperty, BoolProperty, EnumProperty
import os
import re

from .client import request_model
from .gaussian_splatting import import_gs
from .data_collection import track
from.mesh_conversion import generate_mesh, generate_uvs, bake_texture

class GenerateOperator(Operator):
    """Generate 3DGS model"""

    bl_idname = "threegen.generate"
    bl_label = "Generate"

    n_generated: bpy.props.IntProperty(min=0, max=10, default=0)

    def modal(self, context: Context, event: Event):
        threegen = context.window_manager.threegen

        if self.n_generated == threegen.n_generations:
            threegen.in_progress = False
            return {"FINISHED"}

        model_filepath = request_model(threegen.prompt)

        if not model_filepath:
            errmsg = f'Could not generate a model for the prompt "{threegen.prompt}"'
            self.report({"ERROR"}, errmsg)
            track("Generate", {"prompt": threegen.prompt, "success": False, "msg": errmsg})
            return {"CANCELLED"}

        track("Generate", {"prompt": threegen.prompt, "success": True, "msg": ""})
        name = re.sub(r"\s+", "_", threegen.prompt)
        import_gs(model_filepath, name)
        self.n_generated += 1
        threegen.progress = self.n_generated / threegen.n_generations

        return {"PASS_THROUGH"}

    def invoke(self, context: Context, event: Event):
        threegen = context.window_manager.threegen
        track("Generate", {"prompt": threegen.prompt, "count": threegen.n_generations})
        self.n_generated = 0
        threegen.progress = 0.0
        threegen.in_progress = True

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


class ImportOperator(Operator, ImportHelper):
    """Import 3DGS model from file"""

    bl_idname = "threegen.import"
    bl_label = "Import"
    filename_ext = ".ply"

    filter_glob: StringProperty(
        default="*.ply",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ("OPT_A", "First Option", "Description one"),
            ("OPT_B", "Second Option", "Description two"),
        ),
        default="OPT_A",
    )

    def execute(self, context):
        base_name = os.path.basename(self.filepath)
        name, _ = os.path.splitext(base_name)
        name = re.sub(r"\s+", "_", name)
        import_gs(self.filepath, name, "")

        return {"FINISHED"}
    
class MeshConversionOperator(Operator):
    """Create Mesh from 3DGS model"""

    bl_idname = "threegen.generate_mesh"
    bl_label = "Generate Mesh"

    def execute(self, context):
        threegen = context.window_manager.threegen
        gs_obj = context.active_object
        voxel_size = threegen.voxel_size
        adaptivity = threegen.adaptivity
        texture_size = threegen.texture_size
        angle_limit = threegen.angle_limit
        island_margin = threegen.island_margin

        mesh_obj = generate_mesh(gs_obj, voxel_size, adaptivity)
        generate_uvs(mesh_obj, angle_limit, island_margin)
        bake_texture(gs_obj, mesh_obj, texture_size)
        mesh_obj.location.x += mesh_obj.dimensions.x

        return {'FINISHED'}


classes = (
    GenerateOperator,
    ImportOperator,
    MeshConversionOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
