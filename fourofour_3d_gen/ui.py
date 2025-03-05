import bpy
from bpy.types import Context, Panel

from .ops import GenerateOperator, ImportOperator,OpenImageOperator, MeshConversionOperator


class MainPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "Threegen_PT_main"
    bl_label = "3DGS Generation"

    @classmethod
    def poll(cls, context):
        notified = bpy.context.preferences.addons[__package__].preferences.data_collection_notice
        return notified

    def draw(self, context: Context):
        layout = self.layout
        threegen = context.window_manager.threegen

        box = layout.box()
        row = box.row()
        row.operator(OpenImageOperator.bl_idname)
        row = box.row()
        row.prop(threegen, "image", text="")
        row = box.row()
        split = row.split(factor=0.25)

        col = split.column()
        col.prop(threegen, "seed", text="")
        col = split.column()
        col.operator(GenerateOperator.bl_idname)
        row = layout.row()
        row.operator(ImportOperator.bl_idname)



class DisplaySettingsPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "Threegen_PT_settings"
    bl_label = "Splat Display Settings"

    @classmethod
    def poll(cls, context):
        obj = context.object
        notified = bpy.context.preferences.addons[__package__].preferences.data_collection_notice

        return obj is not None and "Gaussian Splatting" in obj.modifiers and notified

    def draw(self, context: Context):
        layout = self.layout
        obj = context.active_object

        row = layout.row()
        row.prop(obj.modifiers["Gaussian Splatting"], '["Socket_4"]', text="Render as point cloud")

        row = layout.row()
        row.prop(obj.modifiers["Gaussian Splatting"], '["Socket_2"]', text="Opacity Threshold")

        row = layout.row()
        row.prop(obj.modifiers["Gaussian Splatting"], '["Socket_3"]', text="Display Percentage")


class ConversionPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "Threegen_PT_conversion"
    bl_label = "Mesh Conversion"

    @classmethod
    def poll(cls, context):
        obj = context.object
        notified = bpy.context.preferences.addons[__package__].preferences.data_collection_notice

        return obj is not None and "Gaussian Splatting" in obj.modifiers and notified

    def draw(self, context: Context):
        threegen = context.window_manager.threegen
        layout = self.layout

        row = layout.row()
        row.prop(threegen, "voxel_size", text="Voxel Size")
        row = layout.row()
        row.prop(threegen, "adaptivity", text="Adaptivity")
        row = layout.row()
        row.prop(threegen, "texture_size", text="Texture Size")    
        row = layout.row()
        op = row.operator(MeshConversionOperator.bl_idname)
        op.voxel_size = threegen.voxel_size
        op.adaptivity = threegen.adaptivity
        op.texture_size = threegen.texture_size


# class ConsentPanel(bpy.types.Panel):
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "404"
#     bl_idname = "Threegen_PT_consent"
#     bl_label = "Data Collection Notice"

#     @classmethod
#     def poll(cls, context: bpy.types.Context) -> bool:
#         notified = bpy.context.preferences.addons[__package__].preferences.data_collection_notice
#         return not notified

#     def draw(self, context: bpy.types.Context):
#         layout = self.layout
#         box = layout.box()
#         text_col = box.column(align=True)
#         text_col.scale_y = 0.8
#         width = context.region.width
#         ui_scale = context.preferences.system.ui_scale
#         for text in utils.wrap_text(const.TRACKING_MSG, (4 / (5 * ui_scale)) * width):
#             text_col.label(text=text)
#         row = layout.row()
#         row.scale_y = 1.5
#         row.operator(ConsentOperator.bl_idname)


class SocialPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "Threegen_PT_social"
    bl_label = "Connect With Us"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context: Context):
        layout = self.layout
        split = layout.split()
        col = layout.column()
        op = col.operator("wm.url_open", text="X/Twitter")
        op.url = "https://x.com/404gen_"
        op = col.operator("wm.url_open", text="Discord")
        op.url = "https://discord.gg/404gen"


classes = (
    MainPanel,
    DisplaySettingsPanel,
    ConversionPanel,
    SocialPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
