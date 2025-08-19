from bpy.types import AddonPreferences, Context, UILayout
from bpy.props import StringProperty, BoolProperty
import bpy
import uuid

from . import dependencies
from . import constants as const
from . import utils


class DependencyInstallationOperator(bpy.types.Operator):
    bl_idname = "threegen.installdeps"
    bl_label = "Install Dependencies"

    def execute(self, context: Context):
        dependencies.install()
        return {"FINISHED"}


class ConsentOperator(bpy.types.Operator):
    """Accept Data Collection"""

    bl_label = "Accept"
    bl_idname = "threegen.consent"

    def execute(self, context: bpy.types.Context) -> set:
        prefs = bpy.context.preferences.addons[__package__].preferences
        prefs.data_collection_notice = True
        if not prefs.uid:
            prefs.uid = str(uuid.uuid4())
        bpy.ops.wm.save_userpref()
        return {"FINISHED"}


class ThreegenPreferences(AddonPreferences):
    bl_idname = __package__
    url: StringProperty(default="https://gateway-us-west.404.xyz:4443")
    token: StringProperty(default="6eca4068-3be6-4d30-b828-f63cda3bc35b")
    uid: StringProperty()
    data_collection: BoolProperty(default=True)
    data_collection_notice: BoolProperty(default=False)

    def draw(self, context: Context):
        layout: UILayout = self.layout
        col = layout.column()
        if dependencies.installed():
            if not self.data_collection_notice:
                width = context.region.width
                ui_scale = context.preferences.system.ui_scale
                for text in utils.wrap_text(const.TRACKING_MSG, 2500):
                    col.label(text=text)
                col.operator(ConsentOperator.bl_idname)
            else:
                col.prop(self, "url", text="URL")
                col.prop(self, "token", text="API Key")
                col.prop(self, "data_collection", text="Allow collection of anonymous usage data")

        else:
            col.operator(DependencyInstallationOperator.bl_idname)


classes = (
    DependencyInstallationOperator,
    ConsentOperator,
    ThreegenPreferences,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
