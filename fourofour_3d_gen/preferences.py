from bpy.types import AddonPreferences, Context, UILayout
from bpy.props import StringProperty
import bpy

class ThreegenPreferences(AddonPreferences):
    bl_idname = __package__
    url: StringProperty(default="https://gateway-us-west.404.xyz")
    token: StringProperty(default="6eca4068-3be6-4d30-b828-f63cda3bc35b")

    def draw(self, context: Context):
        layout: UILayout = self.layout
        col = layout.column()
        col.prop(self, "url", text="URL")
        col.prop(self, "token", text="API Key")

classes = (
    ThreegenPreferences,
)

register, unregister = bpy.utils.register_classes_factory(classes)

