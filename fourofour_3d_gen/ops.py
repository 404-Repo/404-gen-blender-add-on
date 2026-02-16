import bpy
import os,re
from bpy_extras.io_utils import ImportHelper
from bpy.types import Context, Operator
from bpy.props import StringProperty, BoolProperty, EnumProperty

from .util.gaussian_splatting import import_gs

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
        

    
class RemoveJobOperator(Operator):
    """Remove a job from the list"""

    bl_idname = "threegen.remove_job"
    bl_label = "Remove"

    job_id: StringProperty()

    def execute(self, context:Context):
        job_manager = context.window_manager.threegen.job_manager
        job_manager.remove_job(self.job_id)
        print(f"deleting {self.job_id}")
        return {"FINISHED"}
    
class RestartJobOperator(Operator):
    """Restart a failed job from the list"""

    bl_idname = "threegen.restart_job"
    bl_label = "Restart"

    job_id: StringProperty()

    def execute(self, context:Context):
        job_manager = context.window_manager.threegen.job_manager
        job_manager.restart_job(self.job_id)
        print(f"restarting {self.job_id}")
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
        with open(self.filepath, "rb") as f:
            obj = import_gs(f, name)

        return {"FINISHED"}
  

classes = (
    GenerateOperator,
    RemoveJobOperator,
    RestartJobOperator,
    ImportOperator,
    OpenImageOperator,
)

register, unregister = bpy.utils.register_classes_factory(classes)

