import bpy
from bpy.types import Context, Panel, UILayout

from .ops import GenerateOperator, MeshConversionOperator, RemoveTaskOperator, OpenImageOperator
from.preferences import ConsentOperator

class THREEGEN_PT_MainPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_MainPanel"
    bl_label = "Generation"

    def draw_job(self, context:Context, layout:UILayout, job):
        col = layout.column()
        row = col.row()
        row.prop(job, "status", text="")
        row.label(text=job.name)
        row.prop(job, "obj_type", text="")
        op = row.operator(RemoveTaskOperator.bl_idname, text="", icon="TRASH")
        op.job_id = job.id
        row = col.row()
        row.label(text=job.reason)

    def draw_job_list(self, context:Context, layout:UILayout):
        job_manager = context.window_manager.threegen.job_manager
        if not job_manager.has_jobs():
            return
        
        col = layout.column()
        row = col.row()
        row.label(text="Jobs")
        row = col.row()
        col = row.column()
        for job in job_manager.jobs:
            self.draw_job(context, row, job)

    def draw(self, context: Context):
        layout = self.layout
        threegen = context.window_manager.threegen

        row = layout.row()
        row.prop(threegen, "prompt", text="Text")
        if threegen.image:
            row.enabled = False
            if threegen.image_preview:
                row = layout.row()
                col = row.column(align=True)
                col.alignment = 'CENTER'
                col.template_preview(threegen.image_preview, show_buttons=False)
        row = layout.row(align=True)
        row.prop(threegen, "image", text="Image")
        row.operator(OpenImageOperator.bl_idname, text="", icon='IMAGE_DATA')
        row = layout.row()
        row.prop(threegen, "obj_type", expand=True)
        row = layout.row()
        row.prop(threegen, "replace_active_obj", text="Replace active object")
        row = layout.row()
        row.prop(threegen, "include_placeholder_dims", text="Include placeholder size")
        if not threegen.replace_active_obj:
            row.enabled = False  
        row = layout.row()
        row.operator(GenerateOperator.bl_idname)
        row = layout.row()
        self.draw_job_list(context, row)


class THREEGEN_PT_DisplaySettingsPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_DisplaySettingsPanel"
    bl_label = "Splat Display Settings"

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj is not None and "Gaussian Splatting" in obj.modifiers

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
        wm = context.window_manager
        threegen = getattr(wm, "threegen", None)
        if threegen is None:
            return False  # property not yet available

        obj = context.object

        if threegen.obj_type == 'MESH':
            return True

        if obj is not None and "Gaussian Splatting" in obj.modifiers:
            return True

        return False

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
        for text in text.wrap(const.TRACKING_MSG, (4 / (5 * ui_scale)) * width):
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

