import bpy


class WindowManagerProps(bpy.types.PropertyGroup):
    seed: bpy.props.IntProperty(min=1, max=10, default=1)
    progress: bpy.props.FloatProperty(min=0.0, max=1.0, default=0.0)
    in_progress: bpy.props.BoolProperty(default=False)
    image: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Image",
        description="A custom image property"
    )    
    voxel_size: bpy.props.FloatProperty(default=0.005, precision=3)
    adaptivity: bpy.props.FloatProperty(default=0.0, precision=3)

    angle_limit: bpy.props.FloatProperty(default=1.0, precision=3)
    island_margin: bpy.props.FloatProperty(default=0.0, precision=3)

    texture_size: bpy.props.IntProperty(default=4096)
    ray_distance: bpy.props.FloatProperty(default=0.04, precision=3)
    cage_extrusion: bpy.props.FloatProperty(default=0.02, precision=3)

classes = (WindowManagerProps,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.threegen = bpy.props.PointerProperty(type=WindowManagerProps)


def unregister():
    del bpy.types.WindowManager.threegen

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
