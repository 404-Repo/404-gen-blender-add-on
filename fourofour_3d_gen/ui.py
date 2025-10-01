import bpy
from bpy.types import Context, Panel, UILayout

from .client import get_client
from .gateway.gateway_task import GatewayTaskStatus
from .ops import GenerateOperator, MeshConversionOperator, RemoveTaskOperator
from.preferences import ConsentOperator

class THREEGEN_PT_MainPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_MainPanel"
    bl_label = "Generation"

    @classmethod
    def poll(cls, context):
        notified = bpy.context.preferences.addons[__package__].preferences.data_collection_notice
        return notified

    def draw_task_list(self, context:Context, layout:UILayout):
        client = get_client()

        if not client.has_tasks():
            return
        
        col = layout.column()
        row = col.row()
        row.label(text="Tasks")
        row = col.row()
        col = row.column()
        for task in client._tasks:
            row = col.row()
            task_status_icon = "SORTTIME"
            if task.status == GatewayTaskStatus.FAILURE:
                task_status_icon = "ERROR"
            if task.status == GatewayTaskStatus.SUCCESS:
                task_status_icon = "CHECKMARK"           
            row.label(text=task.prompt, icon=task_status_icon)
            task_obj_type_icon = 'OUTLINER_DATA_POINTCLOUD'
            if task.obj_type == 'MESH':
                task_obj_type_icon = 'MESH_DATA'
            row.label(text="", icon=task_obj_type_icon)
            op = row.operator(RemoveTaskOperator.bl_idname, text="", icon="TRASH")
            op.task_id = task.id

    def draw(self, context: Context):
        layout = self.layout
        threegen = context.window_manager.threegen

        row = layout.row()
        row.prop(
            threegen,
            "prompt",
            text="Prompt",
        )
        row = layout.row()
        row.prop(threegen, "obj_type", expand=True)
        row = layout.row()
        row.operator(GenerateOperator.bl_idname)
        row = layout.row()
        self.draw_task_list(context, row)


class THREEGEN_PT_DisplaySettingsPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_DisplaySettingsPanel"
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


class THREEGEN_PT_ConversionPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_ConversionPanel"
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
        row.prop(threegen, "keep_original", text="Keep Original")       
        row = layout.row()
        row.prop(threegen, "voxel_size", text="Min Detail Size")
        row = layout.row()
        row.prop(threegen, "adaptivity", text="Simplify")

        row = layout.row()
        row.prop(threegen, "angle_limit", text="Angle Limit")

        row = layout.row()
        row.prop(threegen, "texture_size", text="Texture Size")

        row = layout.row()
        op = row.operator(MeshConversionOperator.bl_idname)



class THREEGEN_PT_ConsentPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_ConsentPanel"
    bl_label = "Data Collection Notice"

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        notified = bpy.context.preferences.addons[__package__].preferences.data_collection_notice
        return not notified

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        box = layout.box()
        text_col = box.column(align=True)
        text_col.scale_y = 0.8
        width = context.region.width
        ui_scale = context.preferences.system.ui_scale
        for text in utils.wrap_text(const.TRACKING_MSG, (4 / (5 * ui_scale)) * width):
            text_col.label(text=text)
        row = layout.row()
        row.scale_y = 1.5
        row.operator(ConsentOperator.bl_idname)


class THREEGEN_PT_SocialPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_SocialPanel"
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
    THREEGEN_PT_MainPanel,
    THREEGEN_PT_DisplaySettingsPanel,
    THREEGEN_PT_ConversionPanel,
    THREEGEN_PT_SocialPanel,
)

register, unregister = bpy.utils.register_classes_factory(classes)

