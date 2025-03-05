import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Context, Operator, Event
from bpy.props import StringProperty, BoolProperty, EnumProperty
from pathlib import Path
import os
import re

from .client import request_model
from .gaussian_splatting import import_gs
from .data_collection import track
from .mesh_conversion import generate_mesh, generate_uvs, bake_texture

class GenerateOperator(Operator):
    """Generate 3DGS model"""

    bl_idname = "threegen.generate"
    bl_label = "Generate"

    def execute(self, context):
        threegen = context.window_manager.threegen
        img_path = threegen.image.filepath_raw
        name = re.sub(r"\s+", "_", Path(threegen.image.filepath).stem)
        seed = threegen.seed
        model_filepath = request_model(img_path, seed)

        if not threegen.image:
            return {"CANCELLED"}

        if not model_filepath:
            errmsg = f'Could not generate a model for image "{threegen.image.filepath}"'
            self.report({"ERROR"}, errmsg)
            track("Generate", {"image": threegen.image.filepath, "success": False, "msg": errmsg})
            return {"CANCELLED"}
        
        track("Generate", {"image": threegen.image.filepath, "success": True, "msg": ""})
        import_gs(model_filepath, name)

        return {"FINISHED"}
    

class ImportOperator(Operator, ImportHelper):
    """Import 3DGS model from file"""

    bl_idname = "threegen.import"
    bl_label = "Import PLY"
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
        name = Path(self.filepath).stem
        name = re.sub(r"\s+", "_", name)
        import_gs(self.filepath, name, "")

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
        threegen = context.window_manager.threegen
        image_path = self.filepath
        try:
            # Load the image into bpy.data.images
            img = bpy.data.images.load(image_path, check_existing=True)
            threegen.image = img


            self.report({'INFO'}, f"Loaded image: {img.name}")
        except RuntimeError:
            self.report({'ERROR'}, "Could not load image. Check the file path.")
        return {'FINISHED'}

class MeshConversionOperator(Operator):
    """Create Mesh from 3DGS model"""

    bl_idname = "threegen.generate_mesh"
    bl_label = "Generate Mesh"

    voxel_size: bpy.props.FloatProperty(default=0.005)
    adaptivity: bpy.props.FloatProperty(default=0.0)
    texture_size: bpy.props.IntProperty(default=4096)

    def execute(self, context):
        gs_obj = context.active_object
        mesh_obj = generate_mesh(gs_obj, self.voxel_size, self.adaptivity)
        generate_uvs(mesh_obj)
        bake_texture(gs_obj, mesh_obj, self.texture_size)
        mesh_obj.location.x += mesh_obj.dimensions.x

        return {'FINISHED'}

classes = (
    GenerateOperator,
    ImportOperator,
    OpenImageOperator,
    MeshConversionOperator,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
