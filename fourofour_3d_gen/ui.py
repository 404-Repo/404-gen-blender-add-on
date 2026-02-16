import bpy
from bpy.types import Context, Panel, UILayout

from .import ops

job_status_icon = {
    'COMPLETED': 'CHECKMARK',
    'FAILED': 'ERROR',
    'RUNNING': 'SORTTIME'
}

class THREEGEN_PT_MainPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_MainPanel"
    bl_label = "Generation"

    def draw_job(self, context:Context, layout:UILayout, job):
        col = layout.column()
        row = col.row()
        row.label(text="", icon=job_status_icon.get(job.status, 'QUESTION'))
        row.label(text=job.name)
        subrow = row.row(align=True)
        op = subrow.operator(ops.RestartJobOperator.bl_idname, text="", icon="FILE_REFRESH")
        op.job_id = job.id
        subrow.enabled = job.status == 'FAILED'
        op = row.operator(ops.RemoveJobOperator.bl_idname, text="", icon="TRASH")
        op.job_id = job.id
        if job.reason:
            row = col.row()
            row.label(text=job.reason)

    def draw_job_list(self, context:Context, layout:UILayout):
        job_manager = context.window_manager.threegen.job_manager
        if not job_manager.has_jobs():
            return
        
        col = layout.column()
        row = col.row()
        row.label(text="Jobs")
        for job in job_manager.jobs:
            row = col.row()
            self.draw_job(context, row, job)

    def draw(self, context: Context):
        layout = self.layout
        threegen = context.window_manager.threegen

        row = layout.row()
        row.prop(threegen, "prompt", text="Text")
        if threegen.image or threegen.obj_type == 'MESH':
            row.enabled = False
            if threegen.image_preview:
                row = layout.row()
                col = row.column(align=True)
                col.alignment = 'CENTER'
                col.template_preview(threegen.image_preview, show_buttons=False)
        row = layout.row(align=True)
        row.prop(threegen, "image", text="Image")
        row.operator(ops.OpenImageOperator.bl_idname, text="", icon='IMAGE_DATA')
        row = layout.row()
        row.prop(threegen, "obj_type")
        # row = layout.row()
        # row.prop(threegen, "seed", text="Seed")
        # row.prop(threegen, "randomize_seed", text="Random Seed")
        row = layout.row()
        row.prop(threegen, "replace_active_obj", text="Replace active object")
        row = layout.row()
        row.prop(threegen, "include_placeholder_dims", text="Include placeholder size")
        if not threegen.replace_active_obj:
            row.enabled = False  
        row = layout.row()
        row.operator(ops.GenerateOperator.bl_idname)
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


class THREEGEN_PT_IOPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "404"
    bl_idname = "THREEGEN_PT_IOPanel"
    bl_label = "Import/Export"

    def draw(self, context: Context):
        layout = self.layout
        row = layout.row()
        row.operator(ops.ImportOperator.bl_idname, text="Import 3DGS PLY")



classes = (
    THREEGEN_PT_MainPanel,
    THREEGEN_PT_DisplaySettingsPanel,
    THREEGEN_PT_IOPanel,
    THREEGEN_PT_SocialPanel,
)

register, unregister = bpy.utils.register_classes_factory(classes)

