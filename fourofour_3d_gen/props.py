import bpy


def on_image_change(self, context):
    if self.image_preview is None:
        self.image_preview = bpy.data.textures.new("Image Preview", type='IMAGE')
        self.image_preview.extension = 'CLIP'

    self.image_preview.image = self.image
    print("Updated Image Preview")

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
        items=[
            ("3DGS", "3DGS", "3DGS"),
            ("MESH", "Mesh", "Mesh"),
        ],
        default="3DGS"
    )
    replace_active_obj: bpy.props.BoolProperty(default=False)


classes = (WindowManagerProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.threegen = bpy.props.PointerProperty(type=WindowManagerProps)


def unregister():
    del bpy.types.WindowManager.threegen

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
