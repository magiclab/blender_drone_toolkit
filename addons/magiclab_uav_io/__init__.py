bl_info = {
    "name": "MagicLab UAV IO",
    "author": "Bassam Kurdali",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "File->Export",
    "description": "Export/Export Object Animations for UAV Control",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
    }

if "bpy" in locals():
    import importlib
    importlib.reload(uav_export)
    importlib.reload(uav_import)
else:
    from . import uav_export
    from . import uav_import

import bpy
from bpy.props import StringProperty, FloatProperty


class MagicLabUAVIO(bpy.types.AddonPreferences):
    bl_idname = __name__
    module_path = StringProperty(
        default='/usr/lib64/python3.5/site-packages', subtype ='DIR_PATH')

    def draw(self, context):
        layout = self.layout
        layout.label(
            "Blender does not include Yaml, we need to find the module")
        layout.prop(self, "module_path", text="Python Site Packages")


def register():
    def glow_get(self):
        glow = self['glow']
        return 0.5 if 0.3 < glow and glow < 0.7 else int(glow)
    def glow_set(self, value):
        self['glow'] = 0.5 if 0.3 < value and value < 0.7 else int(value)
    def glow_update(self, context):
        pass
    bpy.types.Object.glow = FloatProperty(
        default=0.0, name="glow",
        min=0.0, max=2.0,
        soft_min=0.0, soft_max=2.0,
        set=glow_set, get=glow_get, update=glow_update)
    bpy.utils.register_class(MagicLabUAVIO)
    uav_import.register()
    uav_export.register()


def unregister():
    del(bpy.types.Object.glow)
    bpy.utils.unregister_class(MagicLabUAVIO)
    uav_export.register()
    uav_export.unregister()

if __name__ == "__main__":
    register()
